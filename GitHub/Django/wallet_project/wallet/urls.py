from django.urls import path, include
from rest_framework.routers import DefaultRouter
from wallet.views import WalletViewSet, TransactionViewSet

router = DefaultRouter()
router.register(r'wallets', WalletViewSet)
router.register(r'transactions', TransactionViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
