import contextlib

import stripe.error, pydantic
try:
    from API import settings
except(ImportError, ModuleNotFoundError):
    import settings, models


class StripeProductValidationForm(pydantic.BaseModel):

    product_name: typing.Optional[str]
    product_description: typing.Optional[str]
    product_price: typing.Optional[float]
    product_currency: typing.Optional[str]

    @classmethod
    def get_patterns(cls):
        return {
            "product_name": "^[a-zA-Z0-9]{1,100}$",
            "product_description": "^[a-zA-Z0-9]{1,200}$",
            "product_price": "^[0-9]{1,5}.[0-9]{2}$",
            "product_currency": "^[A-Z]{3}$",
        }

    def validate(cls, *args, **kwargs) -> typing.List[str]:
        InvalidFields: typing.List[str] = []
        for regex, value in cls.get_patterns():
            if not re.match(value, kwargs.get(regex)):
                InvalidFields.append(regex)
        if len(InvalidFields) != 0: raise pydantic.ValidationError()
        else: return cls.__class__(**kwargs)


class StripeProductController(object):

    def __init__(self, **options):
        self.options = options

    def convert_price_to_cents(self, product):
        import forex_python.converter
        try:
            currency = product.product_currency
            course = forex_python.converter.CurrencyRates()
            dollar_rate = course.get_rate(base_cur='USD', dest_cur=currency.upper())
            return round(dollar_rate * amount // 100)
        except(TypeError, ValueError, AttributeError,):
            raise NotImplementedError

    def create_product(self,  product: StripeProductValidationForm) -> typing.Dict[str, str]:
        try:
            newProduct = stripe.Product.create(
                name=product.dict()["product_name"],
                description=product.dict()["product_description"],
                default_price= product.dict()["product_price"],
                images=[
                    product.dict()["product_image_url"],
                ],
                default_price_data={
                'currency': product.product_currency,
                'unit_amount': self.convert_price_to_cents(product=product),
                'recurring': {'interval': 'month'}
                },
                api_key=getattr(settings, "STRIPE_API_SECRET")
            )
            stripeProductInfo = {"stripe_product_credentials": {
                "StripeProductId": newProduct["id"],
                "StripeProductCreatedAt": newProduct["CreatedAt"],
                "StripeProductName": newProduct["name"]
                }
            }
            return stripeProductInfo
        except(stripe.error.InvalidRequestError, AttributeError, KeyError, TypeError):
            raise NotImplementedError

    def update_product(self, updatedData: typing.Dict[str, str]):
        stripe.Product.update(**updatedData)

    def delete_product(self) -> None:
        try:
            stripe.Product.retrieve(
            id=self.subscription.product_id).delete()
        except(stripe.error.StripeError,):
            raise NotImplementedError




