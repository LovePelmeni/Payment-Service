import stripe.error, pydantic
try:
    from API import settings
except(ImportError, ModuleNotFoundError):
    import settings, models

class SubscriptionProduct(object):

    def __init__(self, subscription, **options):
        self.subscription = subscription
        self.options = options

    def convert_to_cents(self, amount, currency):
        import forex_python.converter
        try:
            course = forex_python.converter.CurrencyRates()
            dollar_rate = course.get_rate(base_cur='USD', dest_cur=currency.upper())
            return round(dollar_rate * amount // 100)
        except(TypeError, ValueError, AttributeError,):
            raise NotImplementedError

    def create_product(self) -> stripe.Product:
        try:
            return stripe.Product.create(
                api_key=settings.STRIPE_API_SECRET,
                name=self.subscription.subscription_name,
                default_price_data={
                    'currency': self.subscription.currency,
                    'unit_amount': self.convert_to_cents(self.subscription.amount,
                    self.subscription.currency),
                    'recurring': {'interval': 'month'}
                },
            )
        except(stripe.error.InvalidRequestError, AttributeError, KeyError, TypeError):
            raise NotImplementedError

    def delete_product(self) -> None:
        try:
            stripe.Product.retrieve(
            id=self.subscription.product_id).delete()
        except(stripe.error.StripeError,):
            raise NotImplementedError


