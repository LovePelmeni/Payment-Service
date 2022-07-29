import ormar
from .proto.payments import payment_pb2, payment_pb2_grpc

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
            Data = request.data.get("paymentSessionCredentials")
            paymentSessionCredentials = payment_api.PaymentValidationForm(**Data)
            paymentSessionInitializer = payment_api.PaymentSessionInitializer(paymentSessionCredentials)
            SessionKey = paymentSessionInitializer.create_payment_session()
            return payment_pb2_grpc.PaymentSessionResponse(
            {"SessionKey": SessionKey}
            )
        except(pydantic.ValidationError, ormar.NoMatch) as val_err:

            logger.debug("Invalid Payment Session Credentials. %s" % val_err)
            return payment_pb2.PaymentSessionResponse(
            {"SessionKet": None})


class PaymentIntentController(payment_pb2_grpc.PaymentIntentServicer):

    async def CreatePaymentIntent(self, request, context, insecure=True):
        try:
            paymentSessionCredentialsId = request.data.get("paymentIntentCredentials")
            paymentIntentInitializer = payment_api.PaymentIntentInitializer(paymentSessionCredentialsId)

            PaymentIntentCredentials = paymentIntentInitializer.create_payment_intent()
            return payment_pb2.PaymentIntentResponse(
                {"PaymentIntentSecretId": PaymentIntentCredentials["payment_intent_secret"],
                 "PaymentId": PaymentIntentCredentials["payment_id"]}
            )

        except(ormar.NoMatch, pydantic.ValidationError) as exception:

            logger.debug("Exception Occurred While Processing Payment Intent Form: %s" % exception)
            return payment_pb2_grpc.PaymentIntentResponse({"PaymentIntentId": None, "PaymentId": None})
            # basically returns None (Emtpy String) If Exception Occurs.


class PaymentCheckoutController(object):

    async def CreatePaymentCheckout(self, request, context):
        try:
            paymentId = request.data.get('paymentCheckoutCredentials')
            payment = await models.Payment.objects.get(id=paymentId)
            return payment_pb2_grpc.PaymentCheckoutResponse({'PaymentCheckoutInfo': {
                "PaymentCurrency": payment.currency,
                "Purchaser": payment.purchaser.username,
                "Amount": payment.amount,
                "CreatedAt": datetime.datetime.now(),
                "ChargeId": payment.charge_id,
            }})
        except(ormar.NoMatch, KeyError, AttributeError):
            logger.debug("Payment Does Not Exist...")
            return payment_pb2_grpc.PaymentCheckoutResponse({"PaymentCheckoutInfo": None})
