import os
import re

# Функция для обработки данных из файла
def process_file(input_file):
    with open(input_file, 'r') as file:
        data = file.read()

    # Ищем числа и диапазоны (для этого используем \d+-\d+, в котором "d+" это числа, а "-" знак дефиса)
    numbers = re.findall(r'\d+-\d+|\d+', data)

    # Разбиваем диапазоны чисел на отдельные числа
    expanded_numbers = []
    for number in numbers:
        if '-' in number:
            start, end = map(int, number.split('-'))
            expanded_numbers.extend(range(start, end + 1))
        else:
            expanded_numbers.append(int(number))

    return expanded_numbers

# Папка, где находятся исходные файлы
source_folder = "TEST"
# Папка, куда сохранять результаты
result_folder = os.path.join(source_folder, "Result")

# Создаем папку для результатов, если она не существует, на всякий случай
if not os.path.exists(result_folder):
    os.makedirs(result_folder)

# Поиск и обработка файлов
for root, dirs, files in os.walk(source_folder):
    for file in files:
        # Проверяем имя файла по маске "TEST_*"
        if file.startswith("TEST_"):
            input_file = os.path.join(root, file)
            # Обрабатываем файл и получаем числа из него
            numbers = process_file(input_file)
            # Создаем новое имя файла для результата
            output_file = os.path.join(result_folder, file.replace("TEST_", "TEST_AUCHAN_success_"))
            # Записываем числа в новый файл
            with open(output_file, 'w') as outfile:
                for number in numbers:
                    outfile.write(str(number) + '\n')

print("Обработка завершена. Результаты сохранены в папке 'Result'.")
