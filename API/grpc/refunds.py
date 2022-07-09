from .proto import payment_pb2_grpc
try:
    from API import models
    from API.refunds import refund_api
except(ImportError, ModuleNotFoundError):
    raise NotImplementedError

import logging
logger = logging.getLogger(__name__)

class RefundController(payment_pb2_grpc.RefundServicer):

    def CreateRefund(self, request, context):
        pass
