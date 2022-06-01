from __future__ import annotations
from . import exceptions as api_exceptions, settings
from .settings import application
import pydantic, stripe.error, logging, fastapi, datetime
from fastapi_csrf_protect import CsrfProtect

logger = logging.getLogger(__name__)

class PaymentValidationForm(pydantic.BaseModel):

    subscription_name: str
    subscription_id: int

    purchaser_id: int
    amount: int
    currency: typing.Literal["usd", "rub", "eur"]


class Payment(object):

    def __init__(self, payment_object: PaymentValidationForm, customer: stripe.Customer):
        self.payment_object = payment_object.dict()
        self.customer = customer

    def check_exists(self):
        try:
            return stripe.PaymentIntent.retrieve(id=self.payment_intent.intent_id,
            api_key=settings.STRIPE_API_KEY, client_secret=settings.STRIPE_API_SECRET)
        except(stripe.error.InvalidRequestError,):
            return False

    def get_intent(self):
        try:
            intent = stripe.PaymentIntent.create(
                api_key=settings.STRIPE_API_KEY,
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
        except(stripe.error.InvalidRequestError,) as exception:
            raise exception


@application.post('/session/')
def start_payment_session(request: fastapi.Request, payment_credentials: dict, csrf_protect: CsrfProtect):
    try:
        csrf_protect.get_csrf_from_headers(headers=request.headers)
        assert payment_credentials['currency'] in ('usd', 'rub', 'eur')
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
        after_expiration=None)
        return fastapi.responses.JSONResponse({'session': session})

    except(stripe.error.InvalidRequestError, AssertionError) as exception:
        logger.debug('[PAYMENT SESSION EXCEPTION]: %s' % exception)
        raise api_exceptions.PaymentSessionFailed(reason=exception.args)


@application.post('/intent/')
def get_payment_intent(request: fastapi.Request, payment_credentials: dict):
    try:
        payment = Payment(payment_object=PaymentValidationForm(**payment_credentials),
        customer=stripe.Customer.retrieve(id=request.query_params.get('customer_id'),
        api_key=getattr(settings, 'STRIPE_API_KEY')))

        intent_secret = payment.get_intent().get('intent_id')
        return fastapi.responses.JSONResponse({'intent_id': intent_secret}, status_code=200)

    except(pydantic.ValidationError, stripe.error.InvalidRequestError) as exception:
        logger.error('[PAYMENT INTENT EXCEPTION]: %s' % exception)
        return fastapi.HTTPException(status_code=400, detail='Invalid Credentials.')




