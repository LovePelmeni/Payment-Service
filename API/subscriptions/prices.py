import stripe.error
try:
    from API import settings
except(ImportError):
    import settings
import typing

class SubscriptionPrice(object):

    def __init__(self, product: stripe.Product):
        self.product = product

    def create_price(self):
        try:
            price = stripe.Price.create(
            api_key=settings.STRIPE_API_SECRET,
            unit_amount=self.product,
            product=self.product.id,
            recurring={'interval': 'month'})
            return price
        except(stripe.error.StripeError,):
            raise NotImplementedError

    def delete_price(self, price_id):
        try:
            stripe.Price.retrieve(
            api_key=settings.STRIPE_API_SECRET, id=price_id).delete()
        except(stripe.error.StripeError,):
            raise NotImplementedError