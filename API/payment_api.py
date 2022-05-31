from __future__ import annotations
from . import exceptions as api_exceptions, settings
from .settings import application
import pydantic, stripe, logging, fastapi, datetime
from fastapi_csrf_protect import CsrfProtect
from . import routers

logger = logging.getLogger(__name__)
payment_router = routers.payment_router


class PaymentObject(pydantic.BaseModel):

    subscription_name: str
    subscription_id: int
    purchaser_id: int
    amount: int
    currency: typing.Literal["usd", "rub", "eur"]


class Payment(object):

    def __init__(self, payment_object: PaymentObject, customer: stripe.Customer):
        self.payment_object = payment_object.dict()
        self.customer = customer

    def __delete__(self, instance):
        try:
            getattr(self, 'payment').cancel(
            idempotency_key=getattr(self, 'idempotency_key'))
            logger.debug('payment intent has been canceled.')
        except(AttributeError,):
            pass
        return super().delete(instance)

    def check_exists(self):
        try:
            return stripe.PaymentIntent.retrieve(id=self.payment_intent.intent_id,
            api_key=settings.STRIPE_API_KEY)
        except(AttributeError):
            return False

    def get_intent(self):
        intent = stripe.PaymentIntent.create(
            api_key=settings.STRIPE_API_SECRET,
            amount=self.payment_object.get('amount'),

            payment_method_types=['card'],
            currency=self.payment_object.get('currency'),

            customer=self.customer,
            metadata={
                'subscription_id': self.payment_object.get('subscription_id'),
                'subscription_name': self.payment_object.get('subscription_name'),

                'payment_amount': self.payment_object.get('amount'),
                'purchaser_id': self.payment_object.get('purchaser_id')
            },
        )
        return {'intent_id': intent.get('client_secret')}



@application.post('/session/', tags=['payment'])
def start_payment_session(request: fastapi.Request, payment_credentials: dict, ):
    try:
        # csrf_protect.validate_csrf_in_cookies(request=request)
        assert kwargs['currency'] in ('usd', 'rub', 'eur')
        session = stripe.checkout.Session.create(api_key=getattr(settings, 'STRIPE_API_KEY'),

        success_url = "http://localhost:8081/payment/succeded/",
        cancel_url = request.headers.get('LAST_PAGE_REFERER'),

        line_items = [{
            "price": payment_credentials.get('amount'),
            "quantity": 1,
            "currency": payment_credentials.get('currency'),
            "customer": models.Customer.objects.get(
            id=request.query_params.get('customer_id')).stripe_customer_id
            }],
        metadata={
            "subscription_id": request.session.get('subscription_id'),
            "subscription_name": request.session.get('subscription_name'),
            "purchaser": request.session.get('purchaser'),
            "date": datetime.datetime.now(),
        },
        mode = "payment",
        payment_intent=stripe.PaymentIntent.retrieve(api_key=settings.STRIPE_API_KEY, id=payment_intent_id),
        after_expiration=None,
        )
        return fastapi.responses.JSONResponse({'session_id': session})
    except(stripe.ErrorObject,) as exception:
        raise api_exceptions.PaymentSessionFailed(reason=exception.args)


@application.post('/intent/{customer_id}/', tags=['payment'])
def get_payment_intent(customer_id: str, payment_credentials: dict):
    try:
        payment = Payment(payment_object=PaymentObject(**payment_credentials),
        customer=stripe.Customer.retrieve(id=customer_id, api_key=getattr(settings, 'STRIPE_API_KEY')))
        intent_secret = payment.get_intent().get('intent_id')
        return fastapi.responses.JSONResponse({'intent_id': intent_secret}, status_code=200)

    except(pydantic.ValidationError, stripe.ErrorObject):
        return fastapi.HTTPException(status_code=400, detail='Invalid Credentials.')




