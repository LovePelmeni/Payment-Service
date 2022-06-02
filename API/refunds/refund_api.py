import fastapi_csrf_protect.exceptions
import ormar.exceptions

from API import settings, models
import stripe, logging, fastapi

from API import exceptions as api_exceptions
from API.settings import application
import stripe.error

from fastapi import Depends

logger = logging.getLogger(__name__)

class Refund(object):

    def __init__(self, payment_secret):
        self.payment_secret = payment_secret

    def __new__(cls, **kwargs):
        try:
            assert kwargs.get('payment_secret') is not None
            payment_identifier = kwargs.get('payment_secret')
            cls.check_payment_valid(payment_identifier=payment_identifier)
            return super().__new__(**kwargs)

        except(NotImplementedError, AssertionError):
            raise api_exceptions.PaymentNotFound()

    @classmethod
    def check_payment_valid(cls, payment_identifier):
        try:
            stripe.PaymentIntent.retrieve(api_key=settings.STRIPE_API_KEY,
            client_secret=settings.STRIPE_API_SECRET, id=payment_identifier)
        except(stripe.error.InvalidRequestError,):
            raise NotImplementedError

    @staticmethod
    async def create_refund(payment_secret):
        try:
            return stripe.Refund.create(api_key=getattr(settings, 'STRIPE_API_SECRET'),
            payment_secret=payment_secret).get('id')

        except(stripe.error.InvalidRequestError,) as api_exception:
            logger.error('[REFUND CREATE EXCEPTION]: %s' % api_exception)
            exception = api_exceptions.RefundFailed(reason=api_exception.args)
            raise exception


    @models.database.transaction(force_rollback=True)
    async def create(self):
        try:
            refund_id = await self.create_refund(payment_secret=self.payment_secret)
            await models.Refund.objects.create(refund_id=refund_id)
            await models.Payment.objects.delete(payment_id=self.payment_secret)

        except(stripe.error.InvalidRequestError,) as exception:
            logger.debug('Refund Failed.')
            raise api_exceptions.RefundFailed(
                reason=getattr(exception, 'reason')
            )

@application.post('/create/refund/')
async def make_refund(request: fastapi.Request, csrf_protect: fastapi_csrf_protect.CsrfProtect = Depends()):
    try:
        csrf_protect.validate_csrf_in_cookies(request=request)
        refund = await Refund(payment_secret=request.query_params.get('payment_secret')).create()
        return fastapi.responses.JsonResponse({'refund': refund})

    except(ormar.exceptions.NoMatch,):
        return fastapi.HTTPException(
            status_code=404, detail='No Such Payment Found.'
        )
    except(api_exceptions.RefundFailed, ) as exception:
        raise exception

    except(api_exceptions.PaymentNotFound, ):
        return fastapi.HTTPException(status_code=404)






