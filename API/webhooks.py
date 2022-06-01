import stripe

from .settings import application
import socket, fastapi.requests
from . import exceptions as api_exceptions, settings, models
import stripe.error, logging

logger = logging.getLogger(__name__)

def send_payment_status_response(status: int, payment_intent_id, error=None):
    with socket.create_connection(address=(settings.APP_HOST + '/', settings.APP_PORT)) as socket_connection:
        socket_connection.send(__data=json.dumps({'status': status, 'error': error}))
        socket_connection.close()
    logger.debug('Payment Response Message has been sended to Consumer by Websocket.')


@application.websocket_route(path='/payment/response/{payment_id}/')
async def wait_for_payment_response(websocket: fastapi.WebSocket):
    """After Confirmation of Payment Client Side Redirects to this url in order to wait for response."""
    await websocket.accept()
    data = await websocket.receive_text()
    if data and 'status' in json.loads(data=data).keys():
        await websocket.send_text(json.dumps({'status': json.loads(data).get('status')}))
        await websocket.close()

@models.database.transaction()
@application.post(path='/webhook/payment/')
async def webhook_controller(request: fastapi.Request):
    try:
        if not 'stripe-signature' in request.headers.keys():
            raise stripe.error.SignatureVerificationError(message='Empty', sig_header=None)

        stripe.Webhook.construct_event(payload=request.body,
        sig_header=request.headers.get('stripe-signature'), secret=getattr(settings, 'STRIPE_API_SECRET'))
        payment = await models.Payment.objects.create(payment_intent_id='')
        send_payment_status_response(status=201, payment_intent_id='')

    except(stripe.error.SignatureVerificationError, ValueError) as signature_exception:
        await models.database.transaction.rollback()
        logger.error('[SIGNATURE_WEBHOOK_ERROR]: %s' % signature_exception)
        return fastapi.responses.Response(status_code=500)


