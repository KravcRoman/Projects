def convert_to_percent(rationals):
    for rational in rationals:
        numerator, denominator = map(int, rational.split('/'))
        percent = (numerator / denominator) * 100
        print(f"{percent:.3f}")


n = int(input())  # Rоличество долей
rationals = [input().strip() for _ in range(n)]  # Все доли

convert_to_percent(rationals)
