import fastapi.testclient
import fastapi_csrf_protect.exceptions
import pytest, logging, stripe
from fastapi.security.utils import cs
from API import settings

client = fastapi.testclient.TestClient(app=application)

class TestWebhookEndpoint(pytest.Class):

    def setup(self) -> None:
        self.logger = logging.getLogger(__name__)
        self.session = self.create_http_signature(client)

    @pytest.fixture(scope='module')
    def test_webhook_endpoint(self):
        """Test Module For Stripe Webhook."""
        response = client.post('http://localhost:8081/payment/webhook/')
        assert response.status_code == 200

    @staticmethod
    def create_http_signature(request):
        """Triggers WebHook Request Payment_intent.succeeded"""
        request.headers.update({
        'HTTP_SIGNATURE': stripe.webhook.WebhookSignature()})


class PaymentTestCase(pytest.Class):

    def setup(self) -> None:
        import requests
        self.payment_document = {}
        self.client = requests.Session()
        self.client.headers.update({'CSRF-Token': fastapi_csrf_protect.CsrfProtect(
        ).generate_csrf(secret_key=settings.get_csrf_configuration().secret_key)})

    @pytest.fixture(scope='module')
    def test_get_payment_intent(self):
        import requests
        response = client.post('http://localhost:8081/get/payment/intent/')
        assert response.status_code in ("200", "201")
        assert 'intent_id' in json.loads(response.text).keys()

    @pytest.fixture(scope='module')
    def test_start_payment_session(self):
        import requests
        response = client.post('http://localhost:8081/get/payment/intent/')
        assert response.status_code in ("200", "201")
        assert len(json.loads(response.text).values())


class RefundTestCase(pytest.Class):

    def setup(self) -> None:
        pass

    def test_create_refund(self):
        pass

class StripeCustomerTestCase(pytest.Class):

    def setup(self) -> None:
        pass

    def test_create_stripe_customer(self):
        pass

    def test_delete_stripe_customer(self):
        pass
