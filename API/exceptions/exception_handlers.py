import fastapi_csrf_protect.exceptions

from API.settings import application
import fastapi
from . import exceptions as api_exceptions
import logging

logger = logging.getLogger(__name__)

@application.exception_handler(exc_class_or_status_code=fastapi_csrf_protect.exceptions.CsrfProtectError)
def csrf_exception_handler(request: fastapi.Request, exception: fastapi_csrf_protect.CsrfProtect):
    return fastapi.responses.Response(status_code=403)

@application.exception_handler(exc_class_or_status_code=api_exceptions.InvalidPaymentCredentials)
def invalid_payment_credentials_handler(request: fastapi.Request, exception: api_exceptions.InvalidPaymentCredentials):
    reason = 'Invalid Payment Credentials.'
    if hasattr(exception, 'reason') and getattr(exception, 'reason'):
        reason = exception.reason
    return fastapi.responses.JSONResponse(
        {'error': reason}, status_code=400
    )

@application.exception_handler(exc_class_or_status_code=api_exceptions.InvalidPaymentResponse)
def invalid_payment_response_handler(request: fastapi.Request, exception: api_exceptions.InvalidPaymentResponse):
    from . import webhooks
    reason = 'Payment Responded with Invalid Credentials. Failed. Reason: %s'
    if getattr(exception, 'reason') is not None:
        reason = reason % exception.reason
    webhooks.send_payment_status_response(error=reason, status=500)


@application.exception_handler(exc_class_or_status_code=api_exceptions.PaymentSessionFailed)
def failed_payment_session_handler(request: fastapi.Request, exception: api_exceptions.PaymentSessionFailed):
    reason = getattr(exception, 'reason')
    logger.debug('failed to start new payment session ')
    return fastapi.responses.JSONResponse(
        {'error': 'Failed To Start New Payment Session. Reason: %s' % reason},
        status_code=501
    )

@application.exception_handler(exc_class_or_status_code=api_exceptions.PaymentSessionFailed)
def failed_subscription_creation_handler(request: fastapi.Request, exception: api_exceptions.PaymentSessionFailed):
    logger.error('Exception: %s' % exception)
    return fastapi.responses.Response(status_code=500)

@application.exception_handler(exc_class_or_status_code=api_exceptions.RefundFailed)
def refund_failed_handler(request: fastapi.Request, exception: api_exceptions.RefundFailed):
    reason = 'Refund Failed. Undefined Reason.'
    if getattr(exception, 'reason') is not None:
        reason = 'Refund Failed. Reason: %s' % exception.reason
    return fastapi.responses.JSONResponse(
        {'error': reason}, status_code=500
    )

