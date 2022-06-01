import fastapi.testclient
import fastapi_csrf_protect.exceptions
import pytest, logging, stripe
from fastapi.security.utils import cs
from API import settings
from API import models

client = fastapi.testclient.TestClient(app=application)

class TestWebhookEndpoint(pytest.Class):

    def setup(self) -> None:
        import stripe.webhook
        self.logger = logging.getLogger(__name__)
        self.client = self.create_http_signature(client)

    @pytest.fixture(scope='module')
    def test_webhook_endpoint(self):
        """Test Module For Stripe Webhook."""
        response = self.client.post('http://localhost:8081/webhook/payment/')
        assert response.status_code == 200

    @staticmethod
    def create_http_signature(client):
        """Triggers WebHook Request Payment_intent.succeeded"""
        client.headers.update({
        'stripe-signature': stripe.webhook.WebhookSignature()})
        return client


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
        import requests
        self.payment_secret = stripe.PaymentIntent.create(api_key=getattr(settings, 'STRIPE_API_KEY'),
        client_secret=settings.STRIPE_API_SECRET).get('client_secret')
        self.client = requests.Session()

    @pytest.fixture(scope='module')
    def test_create_refund(self):
        from API import models
        response = requests.post('http://localhost:8081/refund/payment/?payment_secret=%s' % self.payment_secret)
        assert response.status_code == 200
        assert len(models.Refund.objects.all()) == 1


class StripeCustomerTestCase(pytest.Class):

    def setup(self) -> None:
        self.customer_id = models.StripeCustomer.objects.create(username='TestCustomer').id
        self.customer_data = {}
        self.client = requests.Session()

    @pytest.fixture(scope='module')
    def test_create_stripe_customer(self):
        import requests
        response = self.client.post('http://localhost:8081/customer/create/',
        data=self.customer_data)
        assert response.status_code == 200
        assert len(models.StripeCustomer.objects.all()) == 2

    @pytest.fixture(scope='module')
    def test_delete_stripe_customer(self):
        import requests
        response = self.client.delete('http://localhost:8081/customer/delete/?user_id=%s' % self.customer_id)
        assert response.status_code == 200
        assert len(models.StripeCustomer.objects.all()) == 1

