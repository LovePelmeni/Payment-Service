from .proto import payment_pb2_grpc, payment_pb2
try:
    from API import models
    from API.refunds import refund_api
    from API.exceptions import exceptions as api_exceptions
except(ImportError, ModuleNotFoundError):
    raise NotImplementedError

import logging
logger = logging.getLogger(__name__)

class RefundController(payment_pb2_grpc.RefundServicer):

    async def CreateRefund(self, request, context):
        try:
            refundForm = refund_api.Refund(request.ChargeId)
            await refundForm.create()
            return payment_pb2.RefundResponse(True)
        except(ormar.NoMatch, NotImplementedError, api_exceptions.RefundFailed) as exception:
            logger.debug('Failed To Create Refund. Exception Occurred: %s', exception)
            return payment_pb2.RefundResponse(False)



