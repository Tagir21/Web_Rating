import telebot

# Токен вашего бота (получите у @BotFather)
TOKEN = "7507733120:AAHxaTDdpb2y1NS0X0PZjariI3AOsCJYXgQ"

# Создаем экземпляр бота
bot = telebot.TeleBot(TOKEN)

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Я простой бот. Напиши мне что-нибудь.")

# Обработчик любого текстового сообщения
@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, "Привет!")

# Запускаем бота
bot.polling()