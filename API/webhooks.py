import ormar.exceptions
import stripe, json

from .settings import application
import socket, fastapi.requests
from . import exceptions as api_exceptions, settings, models
import stripe.error, logging

logger = logging.getLogger(__name__)

@settings.database.transaction(force_rollback=True)
async def process_success_transaction(paymentCredentials: dict):
    """
    / * Saves transaction to database...
    """
    try:
        payment_payload = paymentCredentials['data']['object']
        await models.Payment.objects.create(
        **payment_payload['metadata'],
        payment_intent_id=payment_payload['client_secret'],

        charge_id=payment_payload['charges']['data'][0]['id'], # charge ID
        subscription=await models.Subscription.objects.get(

        id=payment_payload['metadata']['subscription_id']),
        purchaser=await models.StripeCustomer.objects.get(
        stripe_customer_id=paymentCredentials.get('customer'))
        )

    except(KeyError, AssertionError,) as exception:
        raise exception

@settings.database.transaction(force_rollback=True)
@application.post(path='/webhook/payment/')
async def webhook_controller(request: fastapi.Request):
    try:
        if not 'stripe-signature' in request.headers.keys():
            raise stripe.error.SignatureVerificationError(message='Empty', sig_header=None)
        try:
            stripe.Webhook.construct_event(payload=await request.body(),
            sig_header=request.headers.get('stripe-signature'), secret=getattr(settings, 'STRIPE_API_SECRET'))
        except(stripe.error.SignatureVerificationError,):
            pass

        event = stripe.Event.construct_from(values=json.loads(await request.body()),
        key=settings.STRIPE_API_KEY)

        if event.type in ('payment_intent.succeeded', 'payment_intent.attached'):
            await process_success_transaction(paymentCredentials=event)
        else:
            logger.error('[TRANSACTION FAILED]: not valid payment response')
            raise NotImplementedError

    except(stripe.error.SignatureVerificationError, ValueError,
    NotImplementedError, json.JSONDecodeError) as signature_exception:
        logger.error('[SIGNATURE_WEBHOOK_ERROR]: %s' % signature_exception)
        return fastapi.responses.Response(status_code=500)

    except(KeyError, AttributeError, ormar.exceptions.NoMatch):
        return fastapi.HTTPException(status_code=404)




