import fastapi


class InvalidPaymentCredentials(Exception):

    def __init__(self, invalid_credentials: dict):
        self.invalid_credentials = invalid_credentials

class PaymentValidationError(Exception):

    def __init__(self, invalid_credentials=None):
        self.invalid_credentials = invalid_credentials

class InvalidPaymentResponse(Exception):

    def __init__(self, invalid_credentials=None):
        self.invalid_data = invalid_credentials

class PaymentNotFound(Exception):

    def __call__(self, **kwargs):
        return fastapi.HTTPException(status_code=404)


class PaymentFailed(Exception):

    def __init__(self, reason):
        self.reason = reason

class PaymentSessionFailed(Exception):

    def __init__(self, reason):
        self.reason = reason


class RefundFailed(Exception):

    def __init__(self, reason):
        self.reason = reason

class RefundNotFound(Exception):

    def __call__(self, **kwargs):
        return fastapi.HTTPException(status_code=404)


class CustomerCreationFailed(Exception):

    def __init__(self, reason):
        self.reason = reason


class UserNotFound(Exception):

    def __call__(self, **kwargs):
        return fastapi.HTTPException(status_code=404)

class UserDeletionFailed(Exception):

    def __init__(self, reason):
        self.reason = reason



