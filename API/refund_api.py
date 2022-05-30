import ormar.exceptions
from . import settings, models
import stripe, logging, fastapi
from . import exceptions as api_exceptions

logger = logging.getLogger(__name__)

class Refund(object):

    def __init__(self, payment_secret):
        self.payment_secret = payment_secret

    def __new__(cls, **kwargs):
        try:
            assert kwargs.get('payment_id')
            payment_identifier = kwargs.get('payment_id')
            cls.check_payment_valid(payment_identifier=payment_identifier)
            return super().__new__(**kwargs)
        except(exceptions.PaymentValidationError, exceptions.PaymentDoesNotExist):
            raise api_exceptions.PaymentNotFound()

        except(AssertionError,):
            raise api_exceptions.EmptyPaymentCredentials()

    @classmethod
    def check_payment_valid(cls, payment_identifier):
        return stripe.PaymentIntent.retrieve(id=payment_identifier)

    @staticmethod
    def create_refund(payment_secret):
        try:
            return stripe.Refund.create(api_key=getattr(settings, 'STRIPE_API_KEY'),
            payment_secret=payment_secret).get('id')
        except() as api_exception:
            exception = api_exceptions.RefundFailed(reason=api_exception.args)
            raise exception

    def create(self):
        try:
            refund_id = self.create_refund(payment_secret=self.payment_secret)
            models.Refund.objects.create(refund_id=refund_id)
            models.Payment.objects.delete(payment_id=self.payment_secret)
        except(NotImplementedError,) as exception:
            logger.debug('Refund Failed.')
            raise api_exceptions.RefundFailed(
                reason=getattr(exception, 'reason')
            )

@application.post('refund/payment/{payment_id}/')
def make_refund(payment_secret):
    try:
        refund = Refund(payment_secret=payment_secret).create()
        return fastapi.responses.JsonResponse({'refund': refund})
    except(ormar.exceptions.NoMatch,):
        return fastapi.HTTPException(
            status_code=404, detail='No Such Payment Found.'
        )
    except(api_exceptions.RefundFailed,) as exception:
        raise exception
