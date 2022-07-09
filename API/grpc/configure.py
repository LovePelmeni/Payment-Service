from .proto import payment_pb2_grpc
from . import payments, refunds
import contextlib

class GrpcServer(object):

    def __init__(self, host: str, port: str):
        self.host = host
        self.port = port

    def __call__(self, *args, **kwargs):
        pass

    def registerControllers(self, server):
        pass

    @contextlib.contextmanager
    def runGrpcServer(self):
        yield ""
