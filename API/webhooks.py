import stripe

from .settings import application
import socket, fastapi.requests
from . import exceptions as api_exceptions, routers
import stripe.error, logging

logger = logging.getLogger(__name__)

webhook_router = routers.webhook_router

def send_payment_status_response(status: int, error=None):
    with socket.create_connection(address=(settings.APP_HOST, settings.APP_PORT)) as socket_connection:
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


@application.api_route(path='/payment/')
def webhook_controller(response):
    try:
        if not 'HTTP_STRIPE_SIGNATURE' in response.headers.keys():
            raise stripe.error.SignatureVerificationError(message='Empty', sig_header=None)

        stripe.Webhook.construct_event(payload=response.body,
        sig_header=response.headers.get('HTTP_SIGNATURE'), secret=getattr(settings, 'STRIPE_API_SECRET'))
        send_payment_status_response(status=201)

    except(stripe.error.SignatureVerificationError, ValueError) as signature_exception:
        exception = api_exceptions.InvalidPaymentResponse()
        if hasattr(signature_exception, 'message'):
            exception.response = getattr(signature_exception, 'message')
        raise exception





