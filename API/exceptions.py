import fastapi
class InvalidPaymentCredentials(BaseException):

    def __init__(self, invalid_credentials: dict):
        self.invalid_credentials = invalid_credentials

class PaymentNotFound(BaseException):

    def __call__(self, **kwargs):
        return fastapi.HTTPException(status_code=404)


class PaymentFailed(BaseException):

    def __init__(self, reason):
        self.reason = reason

class PaymentSessionFailed(BaseException):

    def __init__(self, reason):
        self.reason = reason


class RefundFailed(BaseException):

    def __init__(self, reason):
        self.reason = reason

class RefundNotFound(BaseException):

    def __call__(self, **kwargs):
        return fastapi.HTTPException(status_code=404)


class CustomerCreationFailed(BaseException):

    def __init__(self, reason):
        self.reason = reason


class UserNotFound(BaseException):

    def __call__(self, **kwargs):
        return fastapi.HTTPException(status_code=404)

