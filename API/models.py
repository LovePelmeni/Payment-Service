import pydantic, sqlalchemy, ormar, databases
from . import settings

database = databases.Database(url=getattr(settings, 'orm_settings').database_url)
metadata = sqlalchemy.MetaData()

class BaseOrmMetaData(ormar.ModelMeta):
    metadata = metadata
    database = database

class StripeCustomer(ormar.Model):

    class Meta(BaseOrmMetaData):
        table = 'customers'

    id: int = ormar.Integer(primary_key=True)
    stripe_customer_id: str = ormar.String(max_length=100, min_length=1, unique=True, nullable=False)
    active: bool = ormar.Boolean(default=True)


class Payment(ormar.Model):

    class Meta(BaseOrmMetaData):
        table = 'payments'

    id: int = ormar.Integer(primary_key=True)
    payment_intent_id: str = ormar.String(max_length=100, min_length=1, nullable=False)
    subscription_id = ormar.Integer(nullable=False)
    amount: int = ormar.Integer(nullable=False)
    purchaser = ormar.ForeignKey(to=StripeCustomer, nullable=False)

class Refund(ormar.Model):

    class Meta(BaseOrmMetaData):
        table = 'refunds'
    id: int = ormar.Integer(primary_key=True)
    refund_id: str = ormar.String(max_length=100)




