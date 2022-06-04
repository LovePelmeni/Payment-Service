import fastapi_csrf_protect.exceptions
import ormar.exceptions

from API import settings, models
import stripe, logging, fastapi

from API.exceptions import exceptions as api_exceptions
from API.settings import application
import stripe.error

from fastapi import Depends

logger = logging.getLogger(__name__)

class Refund(object):

    def __init__(self, charge_id):
        self.charge_id = charge_id

    @staticmethod
    async def create_refund(charge_id):
        try:
            return stripe.Refund.create(api_key=getattr(settings, 'STRIPE_API_SECRET'),
            charge=charge_id).id

        except(stripe.error.InvalidRequestError, TypeError) as api_exception:
            logger.error('[REFUND CREATE EXCEPTION]: %s' % api_exception)
            exception = api_exceptions.RefundFailed(reason=api_exception.args)
            raise exception


    @settings.database.transaction(force_rollback=True)
    async def create(self):
        try:
            refund_id = await self.create_refund(charge_id=self.charge_id)
            await models.Refund.objects.create(refund_id=refund_id)
            await models.Payment.objects.delete(payment_intent_id=self.charge_id)

        except(stripe.error.InvalidRequestError, TypeError, AttributeError) as exception:
            logger.debug('Refund Failed.')
            raise api_exceptions.RefundFailed(
                reason=getattr(exception, 'reason')
            )

@application.post('/create/refund/')
async def make_refund(request: fastapi.Request, csrf_protect: fastapi_csrf_protect.CsrfProtect = Depends()):
    try:
        csrf_protect.validate_csrf_in_cookies(request=request)
        refund = await Refund(charge_id=request.query_params.get('charge_id')).create()
        return fastapi.responses.JsonResponse({'refund': refund})

    except(ormar.exceptions.NoMatch,):
        return fastapi.HTTPException(
            status_code=404, detail='No Such Payment Found.'
        )
    except(api_exceptions.RefundFailed) as exception:
        raise exception

    except(api_exceptions.PaymentNotFound, KeyError):
        return fastapi.HTTPException(status_code=404)




