def megatrader(n, m, s, days):
    purchased = []
    total_income = 0

    # Проходим по каждому дню и решаем, какие облигации купить
    for day, name, price, quantity in days:
        price_in_units = price / 100 * 1000  # Цена облигации в условных единицах
        total_cost = price_in_units * quantity  # Общая стоимость лота

        if total_cost <= s:  # Если можем купить лот
            purchased.append((day, name, price, quantity))
            total_income += (1000 * quantity)  # Прибавляем доход от погашения облигации
            s -= total_cost  # Уменьшаем оставшиеся средства

    # Выводим результат
    print(total_income)
    for lot in purchased:
        print(f"{lot[0]} {lot[1]} {lot[2]:.1f} {lot[3]}")
    print()


n, m, s = map(int, input().split())  # Читаем количество дней, максимальное количество лотов и сумму
days = []

while True:
    try:
        day_data = input().strip()
        if not day_data:
            break
        day, name, price, quantity = day_data.split()
        price = float(price)
        quantity = int(quantity)
        days.append((int(day), name, price, quantity))
    except EOFError:
        break


megatrader(n, m, s, days)
