import telebot
import random
from telebot import types
# Загружаем список интересных фактов
L = open('C:/Users/kravc/PycharmProjects/FirstProject/venv/GitHub/Links.txt', 'r', encoding='UTF-8')
Links = L.read().split('\n')
L.close()
# Создаем бота
bot = telebot.TeleBot('5884115217:AAFgbZrK6NmxONS8fu4DLYH81VzfA32nXCA')
# Команда start
@bot.message_handler(commands=["start"])
def start(m, res=False):
        # Добавляем кнопку
        markup=types.ReplyKeyboardMarkup(resize_keyboard=True)
        item1=types.KeyboardButton("Интересная ссылка")
        markup.add(item1)
        bot.send_message(m.chat.id, 'Нажми кнопку "Интересная ссылка"',  reply_markup=markup)
# Получение сообщений от юзера
@bot.message_handler(content_types=["text"])
def handle_text(message):
    # Если юзер прислал Интересная ссылка, выдаем ему ссылку
    if message.text.strip() == 'Интересная ссылка':
        answer = random.choice(Links)
    # Отсылаем юзеру сообщение в его чат
        bot.send_message(message.chat.id, answer)
    elif message.text.strip() != 'Интересная ссылка':
        bot.send_message(message.chat.id, 'Нажми кнопку "Интересная ссылка"')
# Запускаем бота
bot.polling(none_stop=True, interval=0)