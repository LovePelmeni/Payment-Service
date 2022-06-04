import fastapi.testclient
import fastapi_csrf_protect.exceptions
import pytest, logging, stripe, json, asgiref.sync
import sqlalchemy, typing, unittest

from sqlalchemy.orm.session import sessionmaker
from sqlalchemy import create_engine

try:
    from API import settings
    from API import models
except(ImportError, ModuleNotFoundError):
    import settings, models


def generate_csrf_token():
    return fastapi_csrf_protect.CsrfProtect().generate_csrf(
    secret_key='payment_secret_key')

class TestClientMixin:
    pass

def create_test_client():
    with fastapi.testclient.TestClient(app=settings.application) as client_session:
        client_session.headers.update({'fastapi-csrf-token': generate_csrf_token()})
        setattr(TestClientMixin, 'client', client_session)

create_test_client()


class TestWebhookEndpoint(TestClientMixin, unittest.TestCase):

    def setUp(self) -> None:
        self.webhook = stripe.webhook.WebhookSignature()
        self.webhook_json_file_path = '/Users/kirillklimushin/PycharmProjects/FastAPIPaymentProject/API/tests/webhook.json'
        self.webhook_json_file = open(self.webhook_json_file_path, mode='rb')

    def generate_http_signature(self):
        import time
        signed_data = '%d,%s' % (int(time.time()), self.webhook_json_file)
        secret = getattr(settings, 'STRIPE_API_SECRET')
        signature = self.stripe_signature = self.webhook._compute_signature(
        payload=signed_data, secret=secret)
        return "t=%s,v1=%s" % (int(time.time()), signature)

    def test_webhook_endpoint(self):
        """Test Module For Stripe Webhook."""
        response = self.client.post('http://localhost:8081/webhook/payment/',
        data=json.dumps(json.load(self.webhook_json_file)).encode('utf-8'),
        headers={'stripe-signature': self.generate_http_signature()}, timeout=10)
        assert response.status_code in (200, 201, 404)


class PaymentTestCase(TestClientMixin, unittest.TestCase):



    def setUp(self) -> None:
        import requests
        self.payment_session_payload = {}
        self.purchaser = models.StripeCustomer.objects.create()
        self.subscription = models.Subscription.objects.create(
        subscription_name='SomeSubscription',
        amount=1000, currency='usd')
        self.payment_intent_payload = {

                'payment_credentials': {
                "subscription_name": self.subscription.subscription_name,
                "subscription_id": self.subscription.id,
                "purchaser_id": self.purchaser.id,
                "amount": self.subscription.amount,
                "currency": self.subscription.currency
            }
        }

    @pytest.mark.asyncio
    async def test_get_payment_intent(self):
        import requests

        self.purchaser = models.StripeCustomer.objects.create()
        self.subscription = models.Subscription.objects.create(
        subscription_name='SomeSubscription',
        amount=1000, currency='usd')

        response = self.client.post('http://localhost:8081/get/payment/intent/',
        data=self.payment_intent_payload, timeout=10,
        headers={'Content-Type': 'application/json'})

        assert all(['payment_id' in json.loads(response.text).keys(),
        'payment_intent_id' in json.loads(response.text).keys()])
        assert response.status_code in ("200", "201")
        assert 'intent_id' in json.loads(response.text).keys()

    @pytest.mark.asyncio
    async def test_start_payment_session(self):
        import requests

        self.purchaser = models.StripeCustomer.objects.create()
        self.subscription = models.Subscription.objects.create(
        subscription_name='SomeSubscription',
        amount=1000, currency='usd')

        response = self.client.post('http://localhost:8081/get/payment/intent/',
        data=self.payment_session_payload, timeout=10)

        assert 'session_id' in json.loads(response.text).keys()
        assert response.status_code in ("200", "201")
        assert len(json.loads(response.text).values())


class RefundTestCase(TestClientMixin, unittest.TestCase):

    def setUp(self) -> None:
        import requests
        self.payment_secret = stripe.PaymentIntent.create(
        api_key=getattr(settings, 'STRIPE_API_SECRET'), amount=1000, currency='usd').get('client_secret')

    def test_create_refund(self):
        from API import models
        response = self.client.post('http://localhost:8081/refund/payment/?charge_id=%s' % self.payment_secret)
        assert response.status_code in (200, 201, 500)
        assert len(models.Refund.objects.all()) == 1


class StripeCustomerTestCase(TestClientMixin, unittest.TestCase):

    def setUp(self) -> None:

        self.customer_data = {}
        self.customer_id = 1

    def test_create_stripe_customer(self):
        import requests
        response = self.client.post('http://localhost:8081/customer/create/',
        data=self.customer_data, timeout=10)
        assert response.status_code in (200, 201)
        assert len(models.StripeCustomer.objects.all()) == 2

    def test_delete_stripe_customer(self):
        import requests
        response = self.client.delete(
        'http://localhost:8081/customer/delete/?user_id=%s' % self.customer_id, timeout=10)
        assert response.status_code in (200, 201, 404)
        assert len(models.StripeCustomer.objects.all()) in (2, 1)


class SubscriptionTestCase(TestClientMixin, unittest.TestCase):

    def setUp(self) -> None:
        self.subscription_data = {
            "subscription_name": "SomeSub",
            "amount": 1000,
            "currency": "usd",
            "subscription_id": 1
        }

    def test_create_subscription(self):
        response = self.client.post('http://localhost:8081/subscription/create/',
        data=self.subscription_data, timeout=10)
        assert response.status_code in (200, 201)

    @pytest.mark.asyncio
    async def test_delete_subscription(self):
        await models.Subscription.objects.create()
        response = await self.client.delete('http://localhost:8081/subscription/delete/',
        params={'subscription_id': self.subscription.id}, timeout=10)
        assert response.status_code in (200, 201, 404)







