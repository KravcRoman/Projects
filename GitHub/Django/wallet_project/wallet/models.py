from django.db import models
from django.contrib.auth.models import User

class Wallet(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wallets')
    currency = models.CharField(max_length=3, choices=(('RUB', 'RUB'), ('USD', 'USD')))
    balance = models.DecimalField(max_digits=10, decimal_places=2)

class Transaction(models.Model):
    sender = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='sent_transactions')
    receiver = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='received_transactions')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)
