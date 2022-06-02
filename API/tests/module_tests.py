import fastapi.testclient
import fastapi_csrf_protect.exceptions
import pytest, logging, stripe
from fastapi.security.utils import cs
from API import settings
from API import models

client = fastapi.testclient.TestClient(app=settings.application)

class TestWebhookEndpoint(pytest.Class):

    def setup(self) -> None:
        import stripe.webhook
        self.logger = logging.getLogger(__name__)
        self.client = self.create_http_signature(client)

    @pytest.fixture(scope='module')
    def test_webhook_endpoint(self):
        """Test Module For Stripe Webhook."""
        response = self.client.post('http://localhost:8081/webhook/payment/')
        assert response.status_code in(200, 201)

    @staticmethod
    def create_http_signature(client):
        """Triggers WebHook Request Payment_intent.succeeded"""
        client.headers.update({
        'stripe-signature': stripe.webhook.WebhookSignature()})
        return client


class PaymentTestCase(pytest.Class):

    def setup(self) -> None:
        import requests
        self.payment_session_payload = {}
        self.payment_intent_payload = {}
        self.client = client
        self.client.headers.update({'CSRF-Token': fastapi_csrf_protect.CsrfProtect(
        ).generate_csrf(secret_key=settings.get_csrf_configuration().secret_key)})

    @pytest.fixture(scope='module')
    def test_get_payment_intent(self):
        import requests
        response = client.post('http://localhost:8081/get/payment/intent/',
        data=self.payment_intent_payload, timeout=10,
        headers={'Content-Type': 'application/json'})

        assert all(['payment_id' in json.loads(response.text).keys(),
        'payment_intent_id' in json.loads(response.text).keys()])
        assert response.status_code in ("200", "201")
        assert 'intent_id' in json.loads(response.text).keys()

    @pytest.fixture(scope='module')
    def test_start_payment_session(self):
        import requests
        response = client.post('http://localhost:8081/get/payment/intent/',
        data=self.payment_session_payload, timeout=10)

        assert 'session_id' in json.loads(response.text).keys()
        assert response.status_code in ("200", "201")
        assert len(json.loads(response.text).values())


class RefundTestCase(pytest.Class):

    def setup(self) -> None:
        import requests
        self.payment_secret = stripe.PaymentIntent.create(api_key=getattr(settings, 'STRIPE_API_KEY'),
        client_secret=settings.STRIPE_API_SECRET).get('client_secret')
        self.client = client

    @pytest.fixture(scope='module')
    def test_create_refund(self):
        from API import models
        response = requests.post('http://localhost:8081/refund/payment/?charge_id=%s' % self.payment_secret)
        assert response.status_code in (200, 500)
        assert len(models.Refund.objects.all()) == 1


class StripeCustomerTestCase(pytest.Class):

    def setup(self) -> None:
        self.customer_id = models.StripeCustomer.objects.create(username='TestCustomer').id
        self.customer_data = {}
        self.client = client

    @pytest.fixture(scope='module')
    def test_create_stripe_customer(self):
        import requests
        response = self.client.post('http://localhost:8081/customer/create/',
        data=self.customer_data, timeout=10)
        assert response.status_code in (200, 201)
        assert len(models.StripeCustomer.objects.all()) == 2

    @pytest.fixture(scope='module')
    def test_delete_stripe_customer(self):
        import requests
        response = self.client.delete(
        'http://localhost:8081/customer/delete/?user_id=%s' % self.customer_id, timeout=10)
        assert response.status_code in (200, 201)
        assert len(models.StripeCustomer.objects.all()) == 1


class SubscriptionTestCase(pytest.Class):

    async def setup(self) -> None:
        self.subscription = await models.Subscription.objects.create()
        self.client = client
        self.subscription_data = {}

    @pytest.fixture(scope='module')
    def test_create_subscription(self):
        response = self.client.post('http://localhost:8081/subscription/create/',
        data=self.subscription_data, timeout=10)
        assert response.status_code in (200, 201)

    @pytest.fixture(scope='module')
    def test_delete_subscription(self):
        response = self.client.delete('http://localhost:8081/subscription/delete/',
        params={'subscription_id': self.subscription.id}, timeout=10)
        assert response.status_code in (200, 201)

