import fastapi
from API import models
import stripe.error
from API.exceptions import exceptions as api_exceptions
@application.post(path='/payment/session/', response_class=fastapi.responses.JSONResponse)
async def start_payment_session(request: fastapi.Request, csrf_protect: CsrfProtect = fastapi.Depends()):
    """
    / * Creates Payment Session for the Subscription and returns
    """
    try:
        csrf_protect.validate_csrf_in_cookies(request=request) if csrf_protect is not None else None
        subscription = await models.Subscription.objects.get(
        id=int(request.query_params.get('subscription_id')))

        customer = await models.StripeCustomer.objects.get(
        id=int(request.query_params.get('customer_id')))
        session = create_payment_session(customer=customer, subscription=subscription)

        return fastapi.responses.JSONResponse(content={'session_id': session.get('id')},
        headers={'Content-Type': 'application/json'}, status_code=201)

    except(stripe.error.InvalidRequestError, AssertionError, KeyError, AttributeError, TypeError) as exception:
        logger.debug('[PAYMENT SESSION EXCEPTION]: %s' % exception)
        raise api_exceptions.PaymentSessionFailed(reason=exception.args)

    except(ormar.exceptions.NoMatch):
        return fastapi.HTTPException(status_code=404)


@application.post(path='/payment/intent/', response_class=fastapi.responses.JSONResponse)  # amount, subscription_id
async def get_payment_intent(request: fastapi.Request, payment_credentials: str = fastapi.Form(),
                             csrf_protect: CsrfProtect = fastapi.Depends()):
    try:
        customer = await models.StripeCustomer.objects.get(id=int(request.query_params.get('customer_id')))
        csrf_protect.validate_csrf_in_cookies(request=request) if csrf_protect is not None else None

        intent_secret = create_payment_intent(
            payment_object=PaymentValidationForm(**json.loads(payment_credentials)), purchaser=customer)
        return fastapi.responses.JSONResponse(intent_secret, status_code=200)

    except(
    pydantic.ValidationError, stripe.error.InvalidRequestError, AttributeError, KeyError, TypeError) as exception:
        logger.error('[PAYMENT INTENT EXCEPTION]: %s' % exception)
        return fastapi.HTTPException(status_code=400, detail='Invalid Credentials.')

    except(fastapi_csrf_protect.exceptions.CsrfProtectError):
        return fastapi.HTTPException(status_code=403)

    except(stripe.error.PermissionError) as exception:
        logger.error('Looks Like Stripe Token is Expired, or try to use secret if you have not still')
        raise exception


@application.get(path='/get/all/user/payments/')
async def get_all_payments(request: fastapi.Request):
    try:
        queryset = await models.StripeCustomer.objects.filter(
            id=request.query_params.get('customer_id')).first().select_related('payments')
        return fastapi.responses.Response(json.dumps({'queryset': queryset}), status_code=200)
    except(ormar.NoMatch):
        return fastapi.HTTPException(status_code=404)
