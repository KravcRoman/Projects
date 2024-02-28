"""
Название программы: Телеграм-бот для управления парсерами через ЦУП
Описание: Управление запуском и контроль сети парсеров
Автор: surfer_liner
Версия: 1.0
Версия Python: 3.11.4
"""

import datetime

import pytz
import telebot
from telebot import types
from flask import Flask

from control_center.control_management_center import finish_parsing_cmc, \
    PARSERS_URLS_DICT, add_cron_job, remove_cron_job, parsers_logs_folder


# FIXME =========================================================== SETTINGS ===
# Токен бота
TOKEN = "6211247463:AAGn70Gdi8Mh5uibC3js79ERjIAC032oRzU"

# Словарь статусов парсеров
parsers_status_dict = {
    'grandline': 'Awaiting Start',
    'severstal': 'Awaiting Start',
    'rosfitting': 'Awaiting Start',
}

# ~~~~~~~~~~~~~~~~~~~~~ КОД ВЫШЕ МЕНЯЕТСЯ ПРИ ИЗМЕНЕНИИ ЭЛЕМЕНТОВ ПРОЕКТА ~~~~~~

# Используемые файлы
launch_plan_path = 'control_center/launch_plan.txt'
# telegram_bot_users_notification_list = 'telegram_bot/' \
#                                        'telegram_bot_users_notification_list.txt'
# telegram_bot_logs_file = 'telegram_bot/telegram_bot_logs.txt'
# parsers_errors = 'control_center/parsers_errors.txt'
# FIXME ========================================================================

# Создаем экземпляр бота
bot = telebot.TeleBot(TOKEN)

# Создаем экземпляр flask-сервера
app = Flask(__name__)


@bot.message_handler(commands=['start'])
def main_menu(message):
    '''
    Обработчик команды /start для вывода главного меню

    Args:
        message (telebot.types.Message): объект сообщения пользователя,
        содержащий команду "/start"
    Returns:
        None
    '''
    # Формируем разметку из кнопок в баре пользователя
    markup = types.ReplyKeyboardMarkup(row_width=2)
    markup.add(types.KeyboardButton('Текущий статус'))
    markup.add(types.KeyboardButton('Сводка'))
    markup.add(types.KeyboardButton('Расписание запуска'))





    # FIXME ВКЛЮЧИ, КОГДА ИСПРАВИШЬ ИМПОРТ В БОТЕ
    # Проверка наличия пользователя в списке ожидающих уведомление об ошибке
    # with open(telegram_bot_users_notification_list, 'r') as f:
    #     lines = f.readlines()
    #     user_id = message.chat.id
    #     lines_dict_without_last_symbols = [int(i[:-1]) for i in lines]
    #     if int(user_id) in lines_dict_without_last_symbols:
    #         markup.add(types.KeyboardButton('Выкл. уведомления об ошибках'))
    #     else:
    #         markup.add(types.KeyboardButton('Вкл. уведомления об ошибках'))




    markup.add(types.KeyboardButton('Остановить парсеры'),
               types.KeyboardButton('Запустить парсеры'))

    # Приветственное сообщение с выводом кнопок
    bot.send_message(message.chat.id, 'Выберите функцию парсеров:',
                     reply_markup=markup)


@bot.message_handler(commands=['start_parsers'])
def start_parsing(message):
    '''
    Обработчик команды /start_parsers для запуска скрипта через CRON

    Args:
        message (telebot.types.Message): объект сообщения пользователя,
        содержащий команду "/start_parsers" или текст "Заупстить парсеры"
    Returns:
        None
    '''
    parsers_answer = add_cron_job()
    bot.send_message(message.chat.id, parsers_answer)


@bot.message_handler(commands=['stop_parsers'])
def stop_parsing(message):
    '''
    Обработчик команды /stop_parsers для удаления задач крона

    Args:
        message (telebot.types.Message): объект сообщения пользователя,
        содержащий команду "/stop_parsers" или текст "Остановить парсеры"
    Returns:
        None
    '''
    # Останавливаем крон
    cron_answer = remove_cron_job()

    # Останавливаем парсеры
    parsers_answer = finish_parsing_cmc()

    # Формируем сообщение
    text_to_sending = parsers_answer + cron_answer

    # Выводим сообщению пользователю
    bot.send_message(message.chat.id, text_to_sending)


def current_status_cmc():
    '''
    Возвращает список с текущим статусом всех парсеров

    Returns:
        parsers_status_dict (dict): Словарь текущих статусов парсеров
    '''
    # Проверяем наличие лог-файла текущего дня
    moscow_time_zone = pytz.timezone('Europe/metinvest')
    moscow_current_date = datetime.datetime.now(moscow_time_zone).date()
    formatted_date = moscow_current_date.strftime('%d-%m-%y.txt')

    # Читаем лог-файл текущих суток
    log_file_path = 'control_center/' + parsers_logs_folder + formatted_date

    try:
        # Создаем файл если его еще не было или читаем файл
        with open(log_file_path, 'a+') as f:
            f.seek(0)
            lines = f.readlines()
            # Сверяем текущий перечень парсеров (parsers_status_dict) с
            # записями парсеров в лог файле
            global parsers_status_dict
            for parser_name, default_status in parsers_status_dict.items():
                count_line = 0
                # Ищем последнюю запись от текущего парсера в лог-файле
                for line in lines:
                    count_line += 1
                    # Если запись от текущего парсера в цикле есть
                    if parser_name in line:
                        # Определяем строку статуса парсера по индексу и
                        # возвращаем её
                        status = lines[count_line][8:-1]
                        # Меняем статус парсера в глобальной области
                        parsers_status_dict[parser_name] = status
        return parsers_status_dict

    # Ловим ошибку функции
    except FileNotFoundError:
        return parsers_status_dict


@bot.message_handler(commands=['status'])
def current_status(message):
    '''
    Обработчик команды /status для проверки текущего статуса парсеров и отправки
    информации пользователю

    Args:
        message (telebot.types.Message): объект сообщения пользователя,
        содержащий команду "/status" или текст "Текущий статус"
    Returns:
        None
    '''
    # Получаем словарь с парсерами и их статусами из ЦУП
    parsers_status_dict = current_status_cmc()

    # Формируем текст для сообщения  суказанием имени парсера и его статуса
    text_to_send = ''
    for parser_name, parser_status in parsers_status_dict.items():
        text_to_send += 'Parsers1: ' + parser_name.upper() + '\nstatus: ' + \
                        parser_status.title() + '\n\n'

    # Отправляем текст пользователю
    bot.send_message(message.chat.id, text_to_send)


def info_logs_cmc(day):
    '''
    Возвращает журналы работы парсеров за указанный день

    Args:
        day (str): дата в формате ДД.ММ, например "20-04"
    Returns:
        str: текстовое описание журнолов работы парсеров за указанный день
        str: в случае отсуствия файла возвращает ее повторный запрос даты
    '''
    # Расчитываем год в москве для его автоматической замены при поиске файла
    # (чтобы не указывать его каждый раз)
    moscow_time_zone = pytz.timezone('Europe/metinvest')
    moscow_current_date = datetime.datetime.now(moscow_time_zone).date()
    formatted_year = moscow_current_date.strftime('-%y.txt')

    # Исключаем ошибку пользователя при вводе разделителя даты
    corrected_date = day[:2] + '-' + day[3:]

    # Формируем путь к лог-файлу
    log_file_path = 'control_center/' + parsers_logs_folder + corrected_date + formatted_year

    try:
        # Извлекаем все логи всех парсеров за указанный день
        with open(log_file_path, 'r') as f:
            f.seek(0)
            lines = f.readlines()
            text_to_send = ''
            for line in lines:
                text_to_send += line
            if text_to_send:
                return text_to_send
            else:
                return 'Записей нет'
    # Обработчик сценария отсутствия файла
    except FileNotFoundError:
        return 'Файл с журналом не найден'


@bot.message_handler(commands=['info'])
def info_logs_menu(message):
    '''
    Обработчик команды /info для получения от пользователя даты для вывода ему
    логов за указанную дату

    Args:
        message (telebot.types.Message): объект сообщения пользователя,
        содержащий команду "/info" или текст "Сводка"
    Returns:
        None
    '''
    # Формируем разметку из кнопок в баре пользователя
    markup = types.ReplyKeyboardMarkup(row_width=2)
    markup.add(types.KeyboardButton('Назад'))

    # Вывод подсказки пользователю
    bot.send_message(message.chat.id, 'Введите дату в формате "ДД-ММ" из '
                                      'которой нужно получить логи пасреров:',
                     reply_markup=markup)

    # Регистрируем следующий шаг для обработки ввода пользоавателя
    bot.register_next_step_handler(message, info_logs)


def info_logs(message):
    '''
    Обработчик для ввода даты пользователем и дальнейшей обработки

    Args:
        message (telebot.types.Message): объект сообщения пользователя,
        содержащий дату
    Returns:
        None
    '''
    # Формируем разметку из кнопок в баре пользователя
    markup = types.ReplyKeyboardMarkup(row_width=2)
    markup.add(types.KeyboardButton('Назад'))

    # Извлекаем дату из сообщения
    date = message.text

    # Проверяем записи на дату
    logs_from_date = info_logs_cmc(date)

    if logs_from_date == 'Записей нет':
        bot.send_message(message.chat.id, logs_from_date)
        main_menu(message)
    else:
        # Если файла нет - возвращаем в главное меню
        if logs_from_date == 'Файл с журналом не найден':
            bot.send_message(message.chat.id, 'Файл с журналом не найден')
            main_menu(message)
        else:
            # Отправляем пользователю логи/ошибку
            bot.send_message(message.chat.id, logs_from_date, reply_markup=markup)


@bot.message_handler(commands=['launch_plan'])
def start_list(message):
    '''
    Обработчик команды /launch_plan для отображения плана запуска и его
    составления

    Args:
        message (telebot.types.Message): объект сообщения пользователя,
        содержащий команду "/launch_plan" или текст "Расписание запуска"
    Returns:
        None
    '''
    # Добавляем кнопки для вывода
    markup = types.ReplyKeyboardMarkup(row_width=2)
    markup.add(types.KeyboardButton('Назад'))
    markup.add(types.KeyboardButton('Изменить расписание'))

    # Достаем из файла расписания парсеры и их время запуска в словарь
    parsers_start_plan_dict = {}
    with open(launch_plan_path, 'r') as f:
        for line in f:
            parts = line.strip().split()
            parser = parts[0]
            start_time = parts[1]
            parsers_start_plan_dict[parser] = start_time

    try:
        # Сортируем словарь парсеров по времени запуска (возрастанию)
        sorted_parsers = sorted(parsers_start_plan_dict.items(),
                                key=lambda x:
                                datetime.datetime.strptime(x[1], '%H:%M'))

        # Формируем сообщение с расписанием
        text_to_send = ''
        count = 1
        for parser_name, parser_start_time in sorted_parsers:
            text_to_send += f'`{count} {parser_name.title():<13} {parser_start_time}\n`'
            count += 1

        # Выводим сообщение пользователю с отсортированными парсерами по времени
        bot.send_message(message.chat.id, text_to_send,
                         reply_markup=markup, parse_mode="Markdown")

    # Обработчик кривого ввода времени от пользователя
    except Exception:
        # Формируем сообщение с расписанием без фильтра
        text_to_send = ''
        count = 1
        for parser_name, parser_start_time in parsers_start_plan_dict.items():
            text_to_send += f'`{count} {parser_name.title():<13} {parser_start_time}\n`'
            count += 1

        # Выводим сообщение с парсерами ползователю
        bot.send_message(message.chat.id, text_to_send,
                         reply_markup=markup, parse_mode="Markdown")


@bot.message_handler(commands=['change_launch_plan_menu'])
def change_launch_plan_menu(message):
    '''
    Обработчик команды /change_launch_plan_menu для вывода кнопок с названиями
    АКТИВНЫХ (включенных в ЦУП, словарь URL) парсеров

    Args:
        message (telebot.types.Message): объект сообщения пользователя,
        содержащий команду "/change_launch_plan_menu" или текст
        "Изменить расписание"
    Returns:
        None
    '''
    # Формируем разметку кнопок
    markup = types.ReplyKeyboardMarkup(row_width=1)

    # Достаем из файла расписания парсеры и их время запуска в словарь
    parsers_start_plan_dict = {}
    with open(launch_plan_path, 'r') as f:
        for line in f:
            parts = line.strip().split()
            parser = parts[0]
            time_start = parts[1]
            parsers_start_plan_dict[parser] = time_start

    try:
        # Сортируем парсеры по времени
        sorted_parsers = sorted(parsers_start_plan_dict.items(),
                                key=lambda x: datetime.datetime.strptime(x[1],
                                '%H:%M'))

        # Создаем клавиши клавиатуры с названиями парсеров в порядке возрастания
        for parser_name, parser_start_time in sorted_parsers:
            markup.add(types.KeyboardButton(f'{parser_name.upper()}'))

        # Выводим кнопки с названиями парсеров и call-action сообщением
        bot.send_message(message.chat.id,
                         'Выберите парсер для корректировки времени запуска:',
                         reply_markup=markup)
    # Обработчик
    except Exception:
        # Создаем клавиши клавиатуры с названиями парсеров в порядке возрастания
        for parser_name, parser_start_time in parsers_start_plan_dict.items():
            markup.add(types.KeyboardButton(f'{parser_name.upper()}'))

        # Выводим кнопки с названиями парсеров и call-action сообщением
        bot.send_message(message.chat.id,
                         'Выберите парсер для корректировки времени запуска:',
                         reply_markup=markup)


parser_name_to_change_start_time = None

@bot.message_handler(commands=['change_launch_plan'])
def change_launch_plan(message):
    '''
    Обработчик команды /change_launch_plan для изменения плана запуска

    Args:
        message (telebot.types.Message): объект сообщения пользователя,
        содержащий команду "/change_launch_plan" или текст "Изменить расписание"
    Returns:
        None
    '''
    # Формируем разметку кнопок
    markup = types.ReplyKeyboardMarkup(row_width=1)
    markup.add(types.KeyboardButton('В меню'))

    # Извлекаем имя парсера из сообщения
    parser_name = message.text.lower()

    global parser_name_to_change_start_time
    parser_name_to_change_start_time = parser_name

    # Выводим кнопку "В меню" и call-action сообщение
    bot.send_message(message.chat.id, 'Введите время запуска в формате чч:мм, часовой пояс Москва:',
                     reply_markup=markup)

    # Регистрируем следующий шаг для обработки ввода пользователя
    bot.register_next_step_handler(message, start_time_change)


def start_time_change(message):
    '''
    Обработчик для ввода времени пользователем и изменении времени запуска
    парсера в расписании

    Args:
        message (telebot.types.Message): объект сообщения пользователя,
        содержащий дату
    Returns:
        None
    '''
    # Формируем разметку кнопок
    markup = types.ReplyKeyboardMarkup(row_width=1)
    markup.add(types.KeyboardButton('В меню'))

    # Достаем из файла расписания парсеры и их время запуска в словарь
    parsers_start_time = {}
    with open(launch_plan_path, 'r') as file:
        for line in file:
            parts = line.strip().split()
            parser = parts[0]
            time_start = parts[1]
            parsers_start_time[parser] = time_start


    if message.text == 'В меню':
        main_menu(message)
    else:
        # Изменение времени у выбранного парсера
        parsers_start_time[parser_name_to_change_start_time] = message.text

        # Изменение времени запуска в файле расписаний.txt (в ЦПУ)
        with open(launch_plan_path, 'w') as file:
            for parser, start_time in parsers_start_time.items():
                file.write(f"{parser} {start_time}\n")


        # Выводим сообщение-уведомление
        bot.send_message(message.chat.id, 'Время запуска исправлено')

        # Направляем пользователя в главное меню
        main_menu(message)






# FIXME ВКЛЮЧИ, КОГДА ИСПРАВИШЬ ИМПОРТ В БОТЕ
# @bot.message_handler(commands=['user_notifications_add'])
# def user_notifications_adder(message):
#     '''
#     Обработчик команды /user_notifications_add для добавления пользователя в
#     список желающих получать уведомления об ошибках
#
#     Args:
#         message (telebot.types.Message): объект сообщения пользователя,
#         содержащий команду "/user_notifications_add" или текст
#         "Включить уведомления об ошибках"
#     Returns:
#         None
#     '''
    #
    # Открываем список, добавляем id чата пользователя
    # with open(telegram_bot_users_notification_list, 'a') as f:
    #     Определяем id чата
        # user_id = str(message.chat.id)
        # Записываем в файл с новой строки
        # f.write(user_id + '\n')

    # Выводим сообщение - уведомление
#    if message.text == 'Вкл. уведомления об ошибках':
#        bot.send_message(message.chat.id, 'Уведомления включены')

    # Возвращаем пользователя в главное меню
#    main_menu(message)

# FIXME ВКЛЮЧИ, КОГДА ИСПРАВИШЬ ИМПОРТ В БОТЕ
# @bot.message_handler(commands=['user_notifications_delete'])
# def user_notifications_deleter(message):
#     '''
#     Обработчик команды /user_notifications_delete для удаления пользователя из
#     списка желающих получать уведомления об ошибках
#
#     Args:
#         message (telebot.types.Message): объект сообщения пользователя,
#         содержащий команду "/user_notifications_add" или текст
#         "Включить уведомления об ошибках"
#     Returns:
#         None
#     '''
#
#     Открываем файл для чтения
    # with open(telegram_bot_users_notification_list, "r") as f:
    #     lines = f.readlines()

    # Создаем новый список строк без строк с указанным содержанием
    # new_lines = [line for line in lines if line.strip() != str(message.chat.id)]

    # Открываем файл для записи и записываем в него новые строки
    # with open(telegram_bot_users_notification_list, "w") as f:
    #     f.writelines(new_lines)

    # Выводим сообщение-уведомление
    # if message.text == 'Выкл. уведомления об ошибках':
    #     bot.send_message(message.chat.id, 'Уведомления отключены')

    # Возвращаем пользователя в главное меню
    # main_menu(message)





@bot.message_handler(func=lambda message: True)
def handle_message(message):
    '''
    Обработчик всех сообщений от пользователя. В зависимости от содержания
    сообщения - она вызывает соответствующие функции для выполнения действий

    Args:
        message (telebot.types.Message): Объект сообщения пользователя
    Returns:
        None
    '''
    if message.text == 'Запустить парсеры':
        start_parsing(message)
    elif message.text == 'Остановить парсеры':
        stop_parsing(message)
    elif message.text == 'Текущий статус':
        current_status(message)
    elif message.text == 'Сводка':
        info_logs_menu(message)
    elif message.text == 'Расписание запуска':
        start_list(message)
    elif message.text == 'Изменить расписание':
        change_launch_plan_menu(message)


    # FIXME ВКЛЮЧИ, КОГДА ИСПРАВИШЬ ИМПОРТ В БОТЕ
    # elif message.text == 'Вкл. уведомления об ошибках':
    #     user_notifications_adder(message)
    # elif message.text == 'Выкл. уведомления об ошибках':
    #     user_notifications_deleter(message)


    elif message.text.lower() in [i for i in PARSERS_URLS_DICT.keys()]:
        change_launch_plan(message)
    elif message.text == 'Назад' or 'В меню':
        main_menu(message)
    else:
        main_menu(message)





# FIXME ВКЛЮЧИ, ЕСЛИ НУЖЕН БУДЕТ ПОСЛЕ ТОГО КАК ИСПРАВИШЬ ИМПОРТ В БОТЕ
# def error_notification(parser_name, status, error):
#     '''
#     Отправляет пользователям подписанным на уведомления об ошибках ошибку от
#     парсера
#
#     Returns:
#         None
#     '''
#
#     Извлекаем id пользователей, подписанных на уведомления об ошибках
#     with open(telegram_bot_users_notification_list, 'r') as f:
    #     for line in f:
    #         bot.send_message(str(line), text_to_send)




while True:
    try:
        bot.polling()
    except Exception as e:
        continue
