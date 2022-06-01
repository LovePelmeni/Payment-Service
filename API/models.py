import typing
import pydantic, sqlalchemy, ormar, databases
import settings

database = databases.Database(url=getattr(settings, 'orm_settings').database_url)
metadata = sqlalchemy.MetaData()

class BaseMetaData(ormar.ModelMeta):

    database = database
    metadata = metadata

@settings.application.on_event('startup')
async def connect_to_database() -> None:
    _database = settings.application.state.database
    if not _database.is_connected:
        await _database.connect()

@settings.application.on_event('shutdown')
async def disconnect_from_database() -> None:
    _database = settings.application.state.database
    if not _database.is_disconnected:
        await _database.disconnect()

class StripeCustomer(ormar.Model):

    class Meta(BaseMetaData):
        tablename = 'customers'

    id: int = ormar.Integer(primary_key=True)
    stripe_customer_id: str = ormar.String(max_length=100, min_length=1, unique=True, nullable=True)
    active: bool = ormar.Boolean(default=True)


class Payment(ormar.Model):

    class Meta(BaseMetaData):
        tablename = "payments"

    id: int = ormar.Integer(primary_key=True)
    payment_intent_id: str = ormar.String(max_length=100, min_length=1, nullable=False)
    subscription_id = ormar.Integer(nullable=False)
    amount: int = ormar.Integer(nullable=False)
    purchaser = ormar.ForeignKey(to=StripeCustomer, nullable=False)


class Refund(ormar.Model):

    class Meta(BaseMetaData):
        tablename = 'refunds'

    id: int = ormar.Integer(primary_key=True)
    refund_id: str = ormar.String(max_length=100)

