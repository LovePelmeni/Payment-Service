import grpc
from .proto import payment_pb2_grpc, payment_pb2
from . import payments, refunds
import contextlib, logging
import futures
import asgiref.sync
import os

GrpcPort = os.getenv("GRPC_PORT")

logger = logging.getLogger(__name__)

class GrpcServer(object):

    def __init__(self, host: str, port: str):
        self.host = host
        self.port = port

    def __call__(self, *args, **kwargs):
        with self.runGrpcServer() as connection:
            self.registerControllers(connection)
            asgiref.sync.sync_to_async(connection.start)()
            asgiref.sync.sync_to_async(asgirefconnection.wait_for_termination)()
            logger.debug('GRPC Server Has been Started....')

    def registerControllers(self, server):
        try:
            payment_pb2_grpc.add_PaymentIntentServicer_to_server(
            servicer=payments.PaymentIntentController, server=server)
            payment_pb2_grpc.add_PaymentSessionServicer_to_server(servicer=payments.PaymentSessionController, server=server)
            payment_pb2_grpc.add_RefundServicer_to_server(servicer=refunds.RefundController, server=server)
            logger.debug('servers has been registered...')

        except(grpc.RpcError) as exception:
            logger.error("GRPC Exception: %s" % exception)

        except(grpc.FutureTimeoutError, grpc.FutureCancelledError,) as exception:
            logger.error("GRPC Server Exception: %s" % exception)


    @contextlib.contextmanager
    def runGrpcServer(self):
        server = grpc.server(thread_pool=futures.ThreadPoolExecutor(max_workers=10))
        server.add_insecure_port(":%s" % GrpcPort)
        yield server


server = GrpcServer(host=GrpcHost, port=GrpcPort)