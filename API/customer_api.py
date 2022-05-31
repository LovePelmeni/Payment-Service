import ormar.exceptions
import stripe, pydantic
from .settings import application
from . import models, settings, exceptions as api_exceptions, routers
import fastapi, requests, logging


logger = logging.getLogger(__name__)
customer_router = routers.customer_router


@models.database.transaction()
@application.post('/create/', tags=['customer'])
def create_customer(request: fastapi.Request):
    try:
        csrf_protect.validate_csrf_in_cookies(request=request)
        # response = requests.post('http://' + settings.SUBSCRIPTION_SERVICE_HOST + '8077/create/customer/', timeout=10)
        # response.raise_for_status()

        customer = models.StripeCustomer.objects.create(**customer_data.dict())
        customer.customer_id = stripe.Customer.create(api_key=getattr(settings, 'STRIPE_API_KEY'),
        params={'customer_id': customer.id})

    except(ormar.exceptions.ModelError, stripe.ErrorObject,

    requests.exceptions.Timeout, NotImplementedError) as exception:
        models.database.transaction.rollback()
        raise api_exceptions.CustomerCreationFailed(reason=str(exception.args))

    customer.save()
    return fastapi.responses.Response(status_code=200)

@models.database.transaction()
@application.delete('delete/', tags=['customer'])
def delete_customer(request: fastapi.Request):
    try:
        csrf_protect.validate_csrf_in_cookies(request=request)
        response = requests.delete('http://' + settings.SUBSCRIPTION_SERVICE_HOST + '8077/delete/customer/', timeout=10)
        response.raise_for_status()

        customer = models.StripeCustomer.objects.get(id=customer_id)
        stripe.Customer.retrieve(api_key=getattr(setting, 'STRIPE_API_KEY'), id=customer.customer_id,
        ).delete(api_key=getattr(settings, 'STRIPE_API_KEY'),
        params={'customer_id': customer.id})

    except(ormar.exceptions.NoMatch, NotImplementedError, requests.exceptions.Timeout) as exception:
        models.database.transaction.rollback()
        raise api_exceptions.UserDeletionFailed(reason=exception.args)






