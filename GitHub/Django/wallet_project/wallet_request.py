import requests

def get_wallets(url):
    """
    Получает список всех кошельков с сервера.

    Args:
    url (str): URL адрес для запроса.

    Returns:
    list: Список всех кошельков, если запрос успешен, иначе None.
    """
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print('Failed to fetch wallets:', response.status_code)
        return None

def create_wallet(url, user_id, currency, balance):
    """
    Создает новый кошелек на сервере.

    Args:
    url (str): URL адрес для запроса.
    user_id (int): ID пользователя, которому принадлежит кошелек.
    currency (str): Валюта кошелька.
    balance (float): Начальный баланс кошелька.

    Returns:
    bool: True, если кошелек успешно создан, иначе False.
    """
    data = {
        'user': user_id,
        'currency': currency,
        'balance': balance
    }
    response = requests.post(url, data=data)
    if response.status_code == 201:
        print('Wallet created successfully!')
        return True
    else:
        print('Failed to create wallet:', response.status_code)
        return False

# URL адрес для запроса кошельков
url = 'http://127.0.0.1:8000/wallet/wallets/'

# Получение списка всех кошельков
wallets = get_wallets(url)
if wallets:
    for wallet in wallets:
        print(wallet)

# Создание нового кошелька
user_id = 2
currency = 'RUB'
balance = 50.00
create_wallet(url, user_id, currency, balance)

