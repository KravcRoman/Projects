# Electronic Wallet App

Это приложение электронного кошелька пользователей с возможностью перевода денежных средств на кошельки других пользователей.

## Использование

### Административная панель Django

1. Перейдите на страницу администратора: `http://127.0.0.1:8000/admin/`
2. Войдите, используя учетные данные администратора (log - admin, pas - admin).
3. Создайте пользователей и кошельки через административную панель.

### API

1. API кошельков: `http://127.0.0.1:8000/wallet/wallets/`, предоставляет возможность получения списка всех кошельков пользователей, а также создания новых кошельков ([wallet_request.py](wallet_request.py)).
2. API транзакций: `http://127.0.0.1:8000/wallet/transactions/`, предоставляет возможность получения списка всех транзакций, а также создания новых транзакций. ([transactions_request.py](transactions_request.py))
