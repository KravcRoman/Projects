from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from wallet.models import Wallet

class WalletTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.wallet = Wallet.objects.create(user=self.user, currency='RUB', balance=100.00)

    def test_wallet_creation(self):
        wallet = Wallet.objects.get(user=self.user)
        self.assertEqual(wallet.currency, 'RUB')
        self.assertEqual(wallet.balance, 100.00)

    def test_api_access(self):
        client = APIClient()
        response = client.get('/wallet/wallets/')
        self.assertEqual(response.status_code, 200)
