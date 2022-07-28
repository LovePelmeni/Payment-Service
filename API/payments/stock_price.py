from API import models
import stripe

class StockPriceCalculator(object):

    def __init__(self, products: typing.List[models.Product]):
        self.products = products

    def getTotalStockPrice(self) -> float:
        price = 0
        for product in self.products:
            productPrice = stripe.Price.retrieve(getattr(settings, "STRIPE_API_SECRET"),
            product_id=json.loads(product.stripe_product_credentials)["productId"])
            price += float(productPrice)
        return price