import stripe.error , pydantic
try:
    from API import settings, models
except(ImportError):
    import settings, models

class Product(object):

    def __init__(self, subscription: models.Subscription):
        self.subscription = subscription

    def create_product(self) -> stripe.Product:
        try:
            return stripe.Product.create(
                api_key=settings.STRIPE_API_SECRET,
                name=self.subscription.subscription_name
            )
        except(stripe.error.StripeError):
            raise NotImplementedError

    def delete_product(self) -> None:
        try:
            stripe.Product.retrieve(
            id=self.subscription.product_id).delete()
        except(stripe.error.StripeError):
            raise NotImplementedError

