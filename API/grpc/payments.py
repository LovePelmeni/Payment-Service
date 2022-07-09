from .proto import payment_pb2_grpc
try:
    from API.payments import payment_api
    from API import models
except(ImportError):
    raise NotImplementedError

import logging
logger = logging.getLogger(__name__)

class PaymentSessionController(payment_pb2_grpc.PaymentSessionServicer):

    async def CreatePaymentSession(self, request, context):
        try:
            paymentSessionCredentials = payment_api.PaymentValidationForm(
            **request.data)

            customer = await models.StripeCustomer.objects.get(
            id=paymentSessionCredentials.dict().get("CustomerId"))
            subscription = await models.Subscription.objects.get(
            id=paymentSessionCredentials.dict().get("SubscriptionId"))

            SessionKey = payment_api.create_payment_session(
            customer=customer, subscription=subscription)
            return payment_pb2_grpc.PaymentSessionResponse(SessionKey=SessionKey)
        except(pydantic.ValidationError, ormar.NoMatch) as val_err:

            logger.debug("Invalid Payment Session Credentials. %s" % val_err)
            return payment_pb2_grpc.PaymentSessionResponse(
            SessionKey=None)

class PaymentIntentController(payment_pb2_grpc.PaymentIntentServicer):

    async def CreatePaymentIntent(self, request, context):
        pass

