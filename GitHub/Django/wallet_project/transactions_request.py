import requests

# URL адрес для запроса транзакций
url = 'http://127.0.0.1:8000/wallet/transactions/'

# Создание новой транзакции
data = {
    'sender': 1,     # ID отправителя
    'receiver': 2,   # ID получателя
    'amount': 50.00  # Сумма транзакции
}

response = requests.post(url, data=data)

if response.status_code == 201:
    print('Transaction created successfully!')
else:
    print('Failed to create transaction:', response.status_code)
    print('Error message:', response.text)  # Вывести сообщение об ошибке, если есть
