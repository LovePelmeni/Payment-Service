from .proto.payments import payment_pb2, payment_pb2_grpc

try:
    from API import models
    from API.refunds import refund_api
    from API.exceptions import exceptions as api_exceptions
except(ImportError, ModuleNotFoundError):
    raise NotImplementedError

import logging
import asgiref.sync
logger = logging.getLogger(__name__)

class RefundController(payment_pb2_grpc.RefundServicer):

    def CreateRefund(self, request, context):
        try:
            refundForm = refund_api.Refund(request.ChargeId)
            asgiref.sync.async_to_sync(refundForm.create)()
            return payment_pb2.RefundResponse(True)
        except(ormar.NoMatch, NotImplementedError, api_exceptions.RefundFailed) as exception:
            logger.debug('Failed To Create Refund. Exception Occurred: %s', exception)
            return payment_pb2.RefundResponse(False)



