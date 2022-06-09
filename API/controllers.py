import http.client
import fastapi, fastapi_csrf_protect
from .settings import application


@application.get('/healthcheck/')
def healthcheck(csrf_protect: fastapi_csrf_protect.CsrfProtect = fastapi.Depends()):
    response = fastapi.responses.Response(status_code=200)
    return response

@application.get('/get/csrf/token/')
def get_csrf_token(csrf_protect: fastapi_csrf_protect.CsrfProtect = fastapi.Depends()):
    response = fastapi.responses.Response(status_code=200)
    csrf_protect.set_csrf_cookie(response=response)
    return response




