import telebot

#initialization of the bot
bot = telebot.TeleBot('7582178055:AAGRAXRJQeLDgIiSF_B7Ui0hm596HhXnuNM')

# /start comand handler
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Я твой новый бот.")

# text message handler
@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, message.text)

# bot starting
bot.polling()