from .proto import payment_pb2_grpc, payment_pb2
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
            return payment_pb2_grpc.PaymentSessionResponse({"SessionKey": SessionKey})
        except(pydantic.ValidationError, ormar.NoMatch) as val_err:

            logger.debug("Invalid Payment Session Credentials. %s" % val_err)
            return payment_pb2.PaymentSessionResponse(
            {"SessionKet": None})


class PaymentIntentController(payment_pb2_grpc.PaymentIntentServicer):

    async def CreatePaymentIntent(self, request, context):
        try:
            paymentCredentials = payment_api.PaymentValidationForm(**request.data)
            customer = await models.StripeCustomer.objects.get(
            id=paymentCredentials.get("CustomerId"))
            PaymentIntentId = payment_api.create_payment_intent(purchaser=customer,
            payment_object=paymentCredentials)
            return payment_pb2.PaymentIntentResponse({"PaymentIntentId": PaymentIntentId})

        except(ormar.NoMatch, pydantic.ValidationError) as exception:

            logger.debug("Exception Occurred While Processing Payment Intent Form: %s" % exception)
            return payment_pb2_grpc.PaymentIntentResponse({"PaymentIntentId": None})
            # basically returns None (Emtpy String) If Exception Occurs.





