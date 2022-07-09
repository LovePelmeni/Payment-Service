import unittest.mock


class GrpcPaymentIntentTestCase(unittest.TestCase):

    def setUp(self) -> None:
        pass

    def getPaymentIntentTestData(self):
        pass

    @unittest.mock.patch("API.grpc.payments.PaymentIntentController.CreatePaymentIntent")
    def TestPaymentIntentCreate(self, mocked_controller):
        pass

    @unittest.mock.patch("API.grpc.payments.PaymentIntentController.CreatePaymentIntent")
    def TestPaymentIntentFailCreate(self, mocked_controller):
        pass


class GrpcPaymentSessionTestCase(unittest.TestCase):

    def setUp(self) -> None:
        pass

    @unittest.mock.patch("API.grpc.payments.PaymentSessionController.CreatePaymentSession")
    def TestPaymentSessionCreate(self, mocked_controller):
        pass

    @unittest.mock.patch("API.grpc.payments.PaymentSessionController.CreatePaymentSession")
    def TestPaymentSessionFailCreate(self, mocked_controller):
        pass


class GrpcRefundSessionTestCase(unittest.TestCase):

    def setUp(self) -> None:
        pass

    @unittest.mock.patch("API.grpc.refunds.RefundController.CreateRefund")
    def TestRefundCreate(self, mocked_controller):
        pass

    @unittest.mock.patch("API.grpc.refunds.RefundController.CreateRefund")
    def TestRefundFailCreate(self, mocked_controller):
        pass