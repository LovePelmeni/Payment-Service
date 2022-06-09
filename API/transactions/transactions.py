import pika

connection = pika.BlockingConnection().channel()


class RabbitmqTransactionController(object):

    def __call__(self, *args, **kwargs) -> typing.Generator:
        yield connection

    def process_success_transaction(self):
        pass

    def process_failed_transaction(self):
        pass

    def keep_process_transaction():
        pass

    def listen_for_response():
        pass

    def listen_for_incoming_transactions(self):
        pass

