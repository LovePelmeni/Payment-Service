import fastapi


payment_router = fastapi.APIRouter(tags=['payment'])

refund_router = fastapi.APIRouter(tags=['refund'])

customer_router = fastapi.APIRouter(tags=['customer'])

webhook_router = fastapi.APIRouter(tags=['webhook'])

healthcheck_router = fastapi.APIRouter(tags=['healthcheck'])

