import ormar
import pydantic, stripe.error, fastapi, json
try:
    from API import settings, models
except(ModuleNotFoundError, ImportError):
    import settings, models

import logging

logger = logging.getLogger(__name__)


HTCI_API_URL = 'https://hcti.io/v1/image/'
HTCI_API_USER_ID = getattr(settings, 'HTCI_API_USER_ID')
HTCI_API_KEY = getattr(settings, 'HTCI_API_KEY')

class PaymentCheckoutImage(object):
    """
    / * Class for Creating Checkout Image from Charge Content
    """

    def __init__(self, payment: models.Payment):
        self.checkout_data = payment

    def get_html_content(self):
        return """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>%s, %s</title>
        </head>
        <body>
        <h1>Amount: %s</<h1>
        <h2>Charge ID: %s</h2>
        </body>
        </html>
        """ % ('Checkout',
        self.checkout_data.purchaser.id, self.checkout_data.amount, self.checkout_data.charge_id)


    def render_to_image(self, content: str, css=None, google_fonts=None):
        """
        / * Using API Creates an image and returns it's url.
        """
        import requests
        try:
            request_image_payload = {'html': content, 'css': css, 'google_fonts': google_fonts}
            response = requests.post(url=HTCI_API_URL, data=request_image_payload,
            timeout=10, auth=(HTCI_API_USER_ID, HTCI_API_KEY))
            return response.json()
        except(requests.exceptions.Timeout, requests.exceptions.RequestException):
            raise NotImplementedError


async def get_streaming_content(content):
    yield content


@settings.application.get('/get/payment/checkout/')
async def get_payment_checkout(request: fastapi.Request):
    try:
        payment_object = await models.Payment.objects.get(
        id=int(request.query_params.get('payment_id')))

        checkout = PaymentCheckoutImage(payment=payment_object)
        checkout_content = checkout.get_html_content()
        checkout_image = checkout.render_to_image(checkout_content)

        return fastapi.responses.JSONResponse(
        content=checkout_image, status_code=200)

    except(pydantic.ValidationError, stripe.error.StripeError, ormar.exceptions.NoMatch) as exception:
        logger.error('[PAYMENT CHECKOUT OBTAIN EXCEPTION] %s' % exception)
        return fastapi.HTTPException(status_code=400)

    except(OSError, NotImplementedError) as exception:
        logger.error('EXCEPTION: %s' % exception)
        return fastapi.HTTPException(status_code=500)





