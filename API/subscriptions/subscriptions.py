import ormar.exceptions
import requests.exceptions, typing
try:
    from API.settings import application
except(ImportError):
    from settings import application
    import settings

import fastapi, pydantic, requests, stripe.error
# from API import models, settings
try:
    from . import products, prices
except(ImportError):
    from . import products, prices

class SubscriptionValidationModel(pydantic.BaseModel):

    subscription_name: str
    amount: int
    currency: typing.Literal["usd", "eur", "rub"]


class SubscriptionViewController(object):

    def __init__(self):
        self.product = products.SubscriptionProduct
        self.price = prices.SubscriptionPrice


    @settings.database.transaction(force_rollback=True)
    @application.post('subscription/create/')
    async def create_subscription(self, subscription_data: str = fastapi.Form()):
        try:

            validated_data = SubscriptionValidationModel(**json.loads(subscription_data))
            await self.apply_stripe_interfaces(models.Subscription(**validated_data.dict())) # applies interfaces
            # and eventually saves the object to the database.
            return fastapi.responses.Response(status_code=201)

        except(ormar.exceptions.ModelError, requests.exceptions.Timeout, NotImplementedError):
            logger.info('could not create')
            return fastapi.HTTPException(status_code=500)


    @settings.database.transaction(force_rollback=True)
    @application.delete('subscription/delete/')
    async def delete_subscription(self, request: fastapi.Request):
        try:

            subscription = models.Subscription.objects.get(id=request.query_params.get('subscription_id'))
            await subscription.unapply_stripe_interfaces()
            await subscription.delete()
            return fastapi.responses.Response(status_code=201)

        except(ormar.exceptions.NoMatch, requests.exceptions.Timeout,
        stripe.error.InvalidRequestError, NotImplementedError):

            logger.info('could not delete subscription, error: %s')
            return fastapi.HTTPException(status_code=500)





