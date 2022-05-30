import stripe

from .settings import application
import websocket
from . import exceptions as api_exceptions
import stripe.error

logger = logging.getLogger(__name__)

def send_payment_status_response(status: int, error=None):
    pass

@application.websocket_route(path='wait/until/payment/response/{payment_id}/')
async def wait_for_payment_response(websocket: fastapi.WebSocket):
    """After Confirmation of Payment Client Side Redirects to this url in order to wait for response."""
    await websocket.accept()
    data = await websocket.receive_text()
    if data and 'status' in json.loads(data=data).keys():
        await websocket.send_text(json.dumps({'status': json.loads(data).get('status')}))
        await websocket.close()

@application.api_route(path='payment/webhook/')
@application.add_exception_handler(exc_class_or_status_code=api_exceptions.PaymentFailed, handler=handle_payment_failed)
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
