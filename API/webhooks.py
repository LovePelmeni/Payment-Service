import stripe, json

from .settings import application
import socket, fastapi.requests
from . import exceptions as api_exceptions, settings, models
import stripe.error, logging

logger = logging.getLogger(__name__)

async def process_success_transaction(paymentCredentials: dict):
    try:
        payment = await models.Payment.objects.create(payment_intent_id=paymentCredentials['metadata']['payment_intent'])
        await payment.purchaser.create(models.StripeCustomer.objects.get(
        stripe_customer_id=paymentCredentials.get('customer')))
    except(KeyError):
        raise NotImplementedError


@models.database.transaction(force_rollback=True)
@application.post(path='/webhook/payment/')
async def webhook_controller(request: fastapi.Request):
    try:
        if not 'stripe-signature' in request.headers.keys():
            raise stripe.error.SignatureVerificationError(message='Empty', sig_header=None)

        stripe.Webhook.construct_event(payload=request.body,
        sig_header=request.headers.get('stripe-signature'), secret=getattr(settings, 'STRIPE_API_SECRET'))

        event = stripe.Event.construct_from(values=json.loads(await request.body()),
        key=settings.STRIPE_API_KEY)

        if event.type in ('payment_intent.succeeded', 'payment_intent.attached'):
            await process_success_transaction(paymentCredentials=event)
        else:
            logger.error('[TRANSACTION FAILED]: not valid payment response')
            raise NotImplementedError

    except(stripe.error.SignatureVerificationError, ValueError, NotImplementedError) as signature_exception:
        logger.error('[SIGNATURE_WEBHOOK_ERROR]: %s' % signature_exception)
        return fastapi.responses.Response(status_code=500)




