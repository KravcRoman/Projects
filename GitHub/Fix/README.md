#   API для расчета бонусов

Сервис для вычисления бонусных баллов пользователям на основе настраиваемых правил, заданных в конфигурационном файле.

##   Установка

1.  **Установите зависимости:**

    ```bash
    pip install -r requirements.txt
    ```

2.  **Настройте правила:**

    - Правила хранятся в файле `bonus_rules.json` (см. `config.py`).
    - Это JSON-файл с правилами, где:
     - ключ — имя правила,
     - значение — параметры и порядок применения (`order`).
      
    **Пример `bonus_rules.json`:**

        ```json
        {
          "base_rate": {"rate": 1, "per_amount": 10, "order": 1},
          "holiday_bonus": {"multiplier": 2, "applies_on": ["Sat", "Sun"], "order": 2},
          "vip_boost": {"multiplier": 1.4, "order": 3}
        }
        ```

## 1.Запуск сервиса

```bash
uvicorn http_service.app:app --reload
```

**Сервис запустится по адресу `http://localhost:8000`.**

## 2.  Отправьте POST-запрос на `/calculate-bonus`:

    - Тело запроса должно быть JSON-объектом со следующими полями:
        - transaction_amount (сумма покупки)
        - timestamp (дата покупки)
        - customer_status (обычный или VIP)

    - Пример запроса с использованием POST /calculate-bonus:
    {
        "transaction_amount": 150,
        "timestamp": "2025-03-08T14:30:00Z",
        "customer_status": "vip"
    }


## 3.  Сервис вернет JSON-ответ:

    -   Ответ будет содержать:
        - Количество начисленных бонусов
        - Какие правила были применены

    -   Пример ответа:
        {
            "total_bonus": 42,
            "applied_rules": [
                {"rule": "base_rate", "bonus": 15},
                {"rule": "holiday_bonus", "bonus": 15},
                {"rule": "vip_boost", "bonus": 12}
           ]
        }
