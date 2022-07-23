import pydantic
from API import models

class ProductUpdateForm(pydantic.BaseModel):
    pass


class ProductValidationForm(pydantic.BaseModel):
    pass


class ProductController(object):

    def createProduct(self, ProductInfo: ProductValidationForm):
        pass

    def updateProduct(self, ProductId: str, ProductUpdatedData: ProductUpdateForm):
        pass

    def deleteProduct(self, ProductId: str):
        pass