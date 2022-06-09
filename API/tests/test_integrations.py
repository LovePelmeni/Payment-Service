import pika
import pytest
try:
    from API import settings
except(ModuleNotFoundError, ImportError):
    import settings

import unittest
class PostgresSQLConnectionChecker(unittest.TestCase):

    def test_connection_established(self):
        import socket
        try:
            connection = socket.create_connection(address=(settings.DATABASE_HOST, settings.DATABASE_PORT))
            connection.close()
        except(socket.timeout):
            raise NotImplementedError


class RabbitmqConnectionChecker(unittest.TestCase):

    def test_connection_established(self):
        import pika.exceptions
        try:
            connection = pika.BlockingConnection(parameters=pika.ConnectionParameters(
            credentials=(settings.RABBITMQ_USER, settings.RABBITMQ_PASSWORD), virtual_host=settings.RABBITMQ_VHOST,
            port=settings.RABBITMQ_PORT, host=settings.RABBITMQ_HOST))
            connection.close()
        except(pika.exceptions.ConnectionClosed, pika.exceptions.AMQPConnectionError,):
            raise NotImplementedError
