import typing
import pydantic, sqlalchemy, ormar, databases
import stripe.error
try:
    from .subscriptions import prices, subscriptions
except(ImportError,):
    from subscriptions import prices, subscriptions

try:
    import settings
except(ModuleNotFoundError):
    from . import settings

metadata = sqlalchemy.MetaData()

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
    if _database.is_disconnected:
        await _database.disconnect()


class StripeCustomer(ormar.Model):

    class Meta(BaseMetaData):
        tablename = 'customers'

    id: int = ormar.Integer(primary_key=True)
    stripe_customer_id: str = ormar.String(max_length=100, min_length=1, unique=True, nullable=True)
    active: bool = ormar.Boolean(default=True)


class Subscription(ormar.Model):
    class Meta(BaseMetaData):
        tablename = "subscriptions"

    id: int = ormar.Integer(primary_key=True)
    product_id: int = ormar.Integer(nullable=True)
    subscription_id: str = ormar.Integer(nullable=False)
    subscription_name: str = ormar.String(max_length=100, min_length=1, nullable=False)
    price_id: int = ormar.Integer(nullable=True)

    async def apply_stripe_interfaces(self):
        """
        / * Creates Product and Price interfaces for the Subscription object.
        // * It is going to be much easier in the future to maintain it, because of ease and availability of this method.
        """
        try:
            product = subscriptions.products.SubscriptionProduct(subscription=self).create_product()
            price = subscriptions.prices.SubscriptionPrice(product=product).create_price()
            for identifier, value in {'product_id': product.id, 'price_id': price.id}.items():
                self.__setattr__(idenitifier, value)
            await self.save()
        except(stripe.error.StripeError, NotImplementedError):
            raise NotImplementedError

    async def unapply_stripe_interfaces(self):
        """
        / * Deletes Product and Price stripe objects before deleting the Model Subscription Object.
        """
        try:
            stripe.Product.retrieve(id=self.product_id, api_key=settings.STRIPE_API_SECRET).delete(id=self.product_id)
        except(stripe.error.StripeError, NotImplementedError):
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
    subscription = ormar.ForeignKey(to=Subscription, nullable=True)
    amount: int = ormar.Integer(nullable=False)
    purchaser = ormar.ForeignKey(to=StripeCustomer, nullable=False, related_name='payments')




