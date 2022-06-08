import ormar
import pydantic, stripe.error, fastapi, json
try:
    from API import settings, models
except(ModuleNotFoundError, ImportError):
    import settings, models

import logging

logger = logging.getLogger(__name__)

class PaymentCheckoutImage(object):
    """
    / * Class for Creating Checkout Image from Charge Content
    """

    def __init__(self, payment: models.Payment):
        self.checkout_data = payment


    def __call__(self, **kwargs):
        return self.render_to_image(content=self.get_html_content())


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


    def render_to_image(self, content: str):
        import weasyprint
        checkout_css = ''
        content = weasyprint.HTML(string=content)
        styles = weasyprint.CSS(string=checkout_css)
        image = content.write_pdf(stylesheets=[styles])
        return image


async def get_streaming_content(content):
    yield content


@settings.application.get('/get/payment/checkout/')
async def get_payment_checkout(request: fastapi.Request):
    try:
        payment_object = await models.Payment.objects.get(
        id=request.query_params.get('payment_id'))

        checkout = PaymentCheckoutImage(payment=payment_object)
        checkout_content = checkout.get_html_content()
        checkout_image = checkout.render_to_image(checkout_content)

        return fastapi.responses.Response(
        content=checkout_image, status_code=200)

    except(pydantic.ValidationError, stripe.error.StripeError, ormar.exceptions.NoMatch) as exception:
        logger.error('[PAYMENT CHECKOUT OBTAIN EXCEPTION] %s' % exception)
        return fastapi.HTTPException(status_code=400)

    except(OSError,) as exception:
        logger.error('OS EXCEPTION: %s' % exception)
        return fastapi.HTTPException(status_code=500)
