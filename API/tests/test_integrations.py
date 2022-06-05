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




