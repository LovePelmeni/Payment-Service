import fastapi_csrf_protect
import ormar.exceptions
import stripe, pydantic

from API.settings import application
from API import models, settings, exceptions as api_exceptions

import fastapi, requests, logging
import stripe.error, asgiref.sync

logger = logging.getLogger(__name__)



@settings.database.transaction(force_rollback=True)
@application.post('/customer/create/')
async def create_customer(request: fastapi.Request, csrf_protect: fastapi_csrf_protect.CsrfProtect = None):
    try:
        csrf_protect.validate_csrf_in_cookies(request=request) if csrf_protect is not None else None
        # response = requests.post('http://' + settings.SUBSCRIPTION_SERVICE_HOST + '8077/create/customer/', timeout=10)
        # response.raise_for_status()

        customer = models.StripeCustomer()
        customer.stripe_customer_id = stripe.Customer.create(api_key=getattr(settings, 'STRIPE_API_SECRET'),
        params={'customer_id': customer.id})['id']

    except(ormar.exceptions.ModelError, stripe.error.InvalidRequestError,
    requests.exceptions.Timeout, NotImplementedError) as exception:

        logger.error('[CREATION USER EXCEPTION]: %s' % exception)
        raise api_exceptions.CustomerCreationFailed(reason=str(exception.args))

    await customer.save()
    return fastapi.responses.Response(status_code=200)



@settings.database.transaction(force_rollback=True)
@application.delete('/customer/delete/')
async def delete_customer(request: fastapi.Request, csrf_protect: fastapi_csrf_protect.CsrfProtect = None):
    try:
        csrf_protect.validate_csrf_in_cookies(request=request) if csrf_protect is not None else None
        # response = requests.delete('http://' + settings.SUBSCRIPTION_SERVICE_HOST + '8077/delete/customer/', timeout=10)
        # response.raise_for_status()

        customer_id = int(request.query_params.get('user_id'))
        customer = await models.StripeCustomer.objects.get(id=customer_id)
        stripe_customer_id = customer.stripe_customer_id

        await customer.delete()
        stripe.Customer.retrieve(api_key=getattr(settings, 'STRIPE_API_KEY'),
        id=stripe_customer_id).delete(api_key=getattr(settings, 'STRIPE_API_KEY'),
        params={'customer_id': customer.id})

        await delete_all_user_payments()

    except(ormar.exceptions.NoMatch, NotImplementedError, requests.exceptions.Timeout, stripe.error.InvalidRequestError,
    ) as exception:
        logger.error('[DELETION USER EXCEPTION]: %s' % exception)
        raise api_exceptions.UserDeletionFailed(reason=exception.args)
