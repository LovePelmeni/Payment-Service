from __future__ import annotations

import logging
import typing

import pydantic, sqlalchemy, ormar, databases
import stripe.error
import stripe

try:
    from . import settings
    from .subscriptions import products
except(ModuleNotFoundError, ImportError):
    import settings
    from subscriptions import products


from sqlalchemy.orm.session import sessionmaker
from sqlalchemy import create_engine

import logging

metadata = sqlalchemy.MetaData()
logger = logging.getLogger(__name__)

engine = sqlalchemy.create_engine(url=settings.orm_settings.database_url)

class BaseMetaData(ormar.ModelMeta):

    database = settings.database
    metadata = metadata


@settings.application.on_event('startup')
async def connect_to_database() -> None:
    _database = settings.application.state.database
    if not _database.is_connected:
        await _database.connect()


@settings.application.on_event('shutdown')
async def disconnect_from_database() -> None:
    _database = settings.application.state.database
    if _database.is_connected:
        await _database.disconnect()


class StripeCustomer(ormar.Model):

    class Meta(BaseMetaData):
        tablename = 'customers'

    id: int = ormar.Integer(primary_key=True)
    stripe_customer_id: str = ormar.String(max_length=100, min_length=1, unique=True, nullable=True)
    active: bool = ormar.Boolean(default=True)



class Product(ormar.Model):

    class Meta(BaseMetaData):
        tablename = "products"

    id: int = ormar.Integer(primary_key=True)
    product_name: str = ormar.String(max_length=100, min_length=1, unique=True, nullable=False)
    product_description: str = ormar.String(max_length=300, min_length=1, unique=False, nullable=True)

    owner = ormar.ForeignKey(to=StripeCustomer, nullable=False, related_name="products")
    product_price: str = ormar.String(max_length=10, min_length=4, regex="^[1-9]{1,5}.[0-9]{2}$")
    currency: str = ormar.String(max_length=5, min_length=3, regex="^[A-Z]{3}$")
    stripe_product_credentials = ormar.JSON() # credentials of the stripe product


    @settings.database.transaction
    def create_instance(self, ProductInfo: ProductInfoValidationForm) -> (bool, Exception):
        try:
            productOwner = asgiref.sync.async_to_sync(models.StripeCustomer.objects.get(
            id=ProductInfo["CustomerId"]))

            newProduct = stripe.Product.create(
                name=ProductInfo.dict()["product_name"],
                description=ProductInfo.dict()["product_description"],
                default_price=ProductInfo.dict()["product_price"],
                images=[
                    ProductInfo.dict()["product_image_url"],
                ],
                api_key=getattr(settings, "STRIPE_API_SECRET")
            )
            ProductInfo.dict().update(**{"stripe_product_credentials": {
                "StripeProductId": newProduct["id"],
                "StripeProductCreatedAt": newProduct["CreatedAt"],
                "StripeProductName": newProduct["name"]
                }
            })

            localTransaction = asgiref.sync.async_to_sync(models.Product.objects.create(
            **ProductInfo.dict(), owner=productOwner))
            return True, localTransaction

        except(ormar.ModelDefinitionError, KeyError, AttributeError) as exception:
            logger.info("Failed to Create Product, Exception Has occurred. %s" % exception)
            settings.database.transaction.rollback()
            return False, exception


    @settings.database.transaction
    def delete_instance(self, ProductId: str) -> (bool, Exception):
        try:
            models.Product.select_for_update() # Locking Object In order to prevent any operations to it..
            product = asgiref.sync.async_to_sync(
            models.Product.objects.get(id=ProductId))

            stripe.Product.delete(**json.loads(
            product.stripe_product_credentials), api_key=getattr(settings, "STRIPE_API_SECRET"))
            return True, None
        except(ormar.exceptions.ModelError, KeyError, AttributeError) as exception:
            logger.info("Failed to Delete Model Instance with Id: %s, Error: %s"
            % ProductId, exception)
            settings.database.transaction.rollback()
            return False, exception


    @settings.database.transaction
    def update_instance(self, ProductUpdatedData: ProductUpdatedForm, ProductId: str) -> (bool, Exception):
        try:
            stripeProductUpdatedFields: typing.Dict[str, str] = {}
            product = asgiref.sync.async_to_sync(models.Product.objects.get(id=ProductId))
            for Property, Value in ProductUpdatedData.dict().items():
                setattr(product, Property, Value)

                if Property in ("product_name", "product_description", "product_price", "currency"):
                    stripeProductUpdatedFields[Property] = Value

            if len(stripeProductUpdatedFields) != 0:
                stripe.Product.update(
                **stripeProductUpdatedFields)

            asgiref.sync.async_to_sync(product.save())
            return True, None

        except(ormar.exceptions.NoMatch, ormar.exceptions.ModelError, KeyError, AttributeError) as exception:
            logger.info("Error While Updating Product Instance, %s" % exception)
            settings.database.transaction.rollback()
            return False, exception


class Subscription(ormar.Model):

    class Meta(BaseMetaData):
        tablename = "subscriptions"

    id: int = ormar.Integer(primary_key=True)
    product_id: str = ormar.String(nullable=True, max_length=100)
    subscription_name: str = ormar.String(max_length=100, min_length=1, nullable=False)

    price_id: str = ormar.String(nullable=True, max_length=100)
    amount: int = ormar.Integer(nullable=True)
    currency: str = ormar.String(nullable=True, max_length=10)


    async def apply_stripe_interfaces(self, **options):
        """
        / * Creates Product and Price interfaces for the Subscription object.
        // * It is going to be much easier in the future to maintain it, because of ease and availability of this method.
        """
        try:
            product = products.SubscriptionProduct(subscription=self, **options).create_product()
            for identifier, value in {'product_id': product.id, 'price_id': product.get('default_price')}.items():
                self.__setattr__(identifier, value)
            await self.save()

        except(stripe.error.StripeError, NotImplementedError) as exception:
            logger.error('could not create product: %s' % exception)
            raise NotImplementedError

    async def unapply_stripe_interfaces(self):
        """
        / * Deletes Product and Price stripe objects before deleting the Model Subscription Object.
        """
        try:
            stripe.Product.retrieve(id=self.product_id, api_key=settings.STRIPE_API_SECRET).update({'active': False})
            stripe.Price.retrieve(id=self.price_id).update({'active': False})

        except(stripe.error.StripeError, NotImplementedError) as exception:
            logger.error('could not delete product: %s' % exception)
            raise NotImplementedError


class Refund(ormar.Model):

    class Meta(BaseMetaData):
        tablename = 'refunds'

    id: int = ormar.Integer(primary_key=True)
    refund_id: str = ormar.String(max_length=100)
    payment_id: str = ormar.Integer(nullable=True)
    purchaser = ormar.ForeignKey(to=StripeCustomer, nullable=True)


class Payment(ormar.Model):

    class Meta(BaseMetaData):
        tablename = "payments"

    id: int = ormar.Integer(primary_key=True)
    payment_intent_id: str = ormar.String(max_length=100, min_length=1, nullable=False)
    charge_id: str = ormar.String(max_length=100, nullable=False)
    subscription = ormar.ForeignKey(to=Subscription, nullable=True)
    amount: int = ormar.Integer(nullable=False)
    purchaser = ormar.ForeignKey(to=StripeCustomer, nullable=False, related_name='payments')




