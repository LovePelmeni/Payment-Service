from __future__ import annotations
import fastapi_csrf_protect.exceptions, json
import typing, json

import ormar.exceptions

from API.exceptions import exceptions as api_exceptions
from API import settings, models
from API.settings import application

import pydantic, stripe.error, logging, fastapi, datetime
from fastapi_csrf_protect import CsrfProtect
from . import stock_price

import asgiref.sync

logger = logging.getLogger(__name__)
stripe.api_key = settings.STRIPE_API_SECRET


class PaymentSessionValidationForm(pydantic.BaseModel):

    product_ids: typing.List[int]
    purchaser_id: int
    amount: float
    currency: typing.Literal["usd", "eur", "rub"]


class PaymentSessionInitializer(object):

    def __init__(self, paymentForm: PaymentSessionValidationForm):
        self.paymentForm = paymentForm
        self.loadedProducts = [asgiref.sync.async_to_sync(models.Product.objects.get)(id=product_id)
         for product_id in self.paymentForm.product_ids]
        self.priceCalculator = stock_price.StockPriceCalculator(self.loadedProducts)


    def create_payment_session(self) -> stripe.checkout.Session:
        return stripe.checkout.Session.create(

            api_key=getattr(settings, 'STRIPE_API_SECRET'),
            success_url=settings.SUCCESS_SESSION_URL,
            cancel_url=settings.CANCEL_SESSION_URL,

            line_items=[{
                "price": self.priceCalculator.getStockTotalPrice(),
                "quantity": len(self.loadedProducts),
            }],
            metadata={
                "product_ids": self.paymentForm.product_ids,
                "product_names": json.dumps([product.product_name for product in self.loadedProducts]),
                "purchaser_id": self.paymentForm.purchaser_id,
                "date": datetime.datetime.now(),
            },
            customer=stripe.Customer.retrieve(id=customer.stripe_customer_id,
            api_key=getattr(settings, "STRIPE_API_SECRET")),
            mode="subscription",
            after_expiration=None)



class PaymentIntentInitializer(object):

    def __init__(self, PaymentSessionId: str):
        try:
            self.PaymentSession = stripe.checkout.Session.get(PaymentSessionId)
        except(stripe.error.StripeError) as exception:
            logger.debug("Invalid Payment Session: %s" % exception)

    def create_payment_intent(self) -> dict:

        try:
            intent = stripe.PaymentIntent.create(
                api_key=settings.STRIPE_API_SECRET,
                amount=self.PaymentSession.get("amount"),

                payment_method_types=['card'],
                currency=self.PaymentSession.get("currency"),

                customer=stripe.Customer.retrieve(id=self.PaymentSession["customer"],
                api_key=settings.STRIPE_API_SECRET),
                stripe_account=getattr(settings, "STRIPE_ACCOUNT_LINK"),
                stripe_version=getattr(settings, "STRIPE_VERSION"),

                metadata={
                    'paymentSessionCredentials': self.PaymentSession["metadata"]
                },
            )
            intent.metadata.update({'payment_id': intent.get('client_secret')})
            return {'payment_client_secret': intent.get('client_secret'),
            'payment_id': intent.id}
        except(stripe.error.InvalidRequestError, KeyError, AttributeError, TypeError) as exception:
            raise exception

