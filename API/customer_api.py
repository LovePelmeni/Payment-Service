import ormar.exceptions
import stripe, pydantic
from . import models, settings, exceptions as api_exceptions
import fastapi
from .settings import application

logger = logging.getLogger(__name__)

@application.post('create/customer/')
def create_customer(customer_data=dict):
    try:
        customer = models.StripeCustomer.objects.create(**customer_data.dict())
        customer.customer_id = stripe.Customer.create(api_key=getattr(settings, 'STRIPE_API_KEY'),
        params={'customer_id': customer.id})
        customer.save()
    except(ormar.exceptions.ModelError, stripe.ErrorObject) as exception:
        raise api_exceptions.CustomerCreationFailed(reason=str(exception.args))

@application.delete('delete/customer/')
def delete_customer(customer_id):
    try:
        customer = models.StripeCustomer.objects.get(id=customer_id)
        stripe.Customer.retrieve(api_key=getattr(setting, 'STRIPE_API_KEY'), id=customer.customer_id,
        ).delete(api_key=getattr(settings, 'STRIPE_API_KEY'),
        params={'customer_id': customer.id})
    except(ormar.exceptions.NoMatch, stripe.ErrorObject):
        raise api_exceptions.UserNotFound()


