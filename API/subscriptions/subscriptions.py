import ormar.exceptions
import requests.exceptions, typing
try:
    from API.settings import application
    from API import settings, models
except(ImportError, ModuleNotFoundError):
    from settings import application
    import settings

import fastapi, pydantic, requests, stripe.error
# from API import models, settings
try:
    from . import products
except(ImportError, ModuleNotFoundError):
    pass

import logging
logger = logging.getLogger(__name__)


class SubscriptionValidationModel(pydantic.BaseModel):

    subscription_name: str
    amount: int
    currency: typing.Literal["usd", "eur", "rub"]

    @pydantic.validator('amount')
    def validate_amount(cls, value):
        return int(value)

async def sub_distributed_transaction(method, url_address, credentials: dict):
    """
    / * Sends The Request To the `url_address` parameter to continue the distributed transaction chain.
    // * Used for creates distributed 'Subscription' objects across bunch of services.
    """
    import requests
    session = requests.Session()
    response = session.request(method=method, url=url_address,
    params=credentials, data=credentials, timeout=20)
    response.raise_for_status()


@settings.database.transaction(force_rollback=True)
@application.post('/subscription/create/')
async def create_subscription(subscription_data: str = fastapi.Form()):
    try:
        import json
        validated_data = SubscriptionValidationModel(**json.loads(subscription_data))
        new_subscription = models.Subscription(**validated_data.dict())
        await new_subscription.apply_stripe_interfaces() # applies interfaces
        # and eventually saves the object to the database.
        return fastapi.responses.Response(status_code=201)

    except(pydantic.ValidationError,
    requests.exceptions.Timeout, NotImplementedError) as exception:
        logger.error('could not create subscription: %s' % exception)
        return fastapi.HTTPException(status_code=500, detail={'errors': exception})


@settings.database.transaction(force_rollback=True)
@application.delete('/subscription/delete/')
async def delete_subscription(request: fastapi.Request):
    try:
        subscription = await models.Subscription.objects.get(id=int(request.query_params.get('subscription_id')))
        await subscription.unapply_stripe_interfaces()
        await subscription.delete()
        return fastapi.responses.Response(status_code=201)

    except(ormar.exceptions.NoMatch, requests.exceptions.Timeout,
    stripe.error.InvalidRequestError,) as exception:

        logger.error('could not delete subscription, error: %s' % exception)
        return fastapi.HTTPException(status_code=500)



