import telebot
from telebot import types
import logging
import time

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Инициализация бота
bot = telebot.TeleBot('7582178055:AAGRAXRJQeLDgIiSF_B7Ui0hm596HhXnuNM')

# Создание меню команд бота
def set_commands():
    commands = [
        types.BotCommand("start", "Начать работу с ботом"),
        types.BotCommand("support", "Написать в техническую поддержку"),
        types.BotCommand("new_task", "Выполнить новое задание")
    ]
    bot.set_my_commands(commands)

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    # Создание клавиатуры
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    dpp_btn = types.KeyboardButton('ДПП')
    db_btn = types.KeyboardButton('Базы Данных')
    archmod_btn = types.KeyboardButton('Архитектурное Моделирование')
    custom_btn = types.KeyboardButton('Кастомная работа')
    
    markup.row(dpp_btn, db_btn)
    markup.row(archmod_btn)
    markup.row(custom_btn)

    welcome_text = """Привет! 👋
    
Я бот-помощник для студентов ББИ. 

Я могу помочь с выполнением практических и лабораторных работ по следующим предметам:
- ДПП
- Базы Данных
- Архитектурное Моделирование
Если необходимого предмета нет в списке:
- Кастомная работа

Выберите предмет, по которому нужно выполнить работу:"""
    
    bot.send_message(message.chat.id, welcome_text, reply_markup=markup)

# Обработчик выбора предмета
@bot.message_handler(content_types=['text'])
def handle_subject_selection(message):
    try:
        if message.text.startswith('/'): 
            return
        
        if message.text == 'Новое задание':
            return new_task(message)
        elif message.text == 'Поддержка':
            return support(message)
        elif message.text in ['ДПП', 'Базы Данных', 'Архитектурное Моделирование', 'Кастомная работа']:
            user_subject = message.text
            
            markup = types.ReplyKeyboardRemove()
            bot.send_message(message.chat.id, 
                            f"Вы выбрали предмет: {user_subject}\n\n"
                            "Пожалуйста, опишите задание подробно:\n"
                            "- Полное название задания\n"
                            "- Сроки выполнения\n"
                            "- Ссылка на задание на Moodle\n"
                            "- Дополнительные требования",
                            reply_markup=markup)
            
            # Регистрация следующего шага
            bot.register_next_step_handler(message, get_task_details)
    except Exception as e:
        logger.error(f"Ошибка в handle_subject_selection: {e}")
        bot.reply_to(message, "Произошла ошибка. Пожалуйста, попробуйте еще раз или обратитесь в поддержку.")

# Обработчик деталей задания
def get_task_details(message):
    if message.text and message.text.startswith('/'):
        if message.text == '/support':
            return support(message)
        elif message.text == '/new_task':
            return new_task(message)
        return

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    new_task_btn = types.KeyboardButton('Новое задание')
    support_btn = types.KeyboardButton('Поддержка')
    markup.row(new_task_btn, support_btn)
    
    bot.reply_to(message, 
                 "Спасибо за предоставленную информацию!\n"
                 "Заявка принята!\n\n"
                 "После утверждения заявки я пришлю вам уведомление.\n\n"
                 "• Стоимость любой работы - 1000 рублей\n"
                 "• Инструкции по оплате - в уведомлении\n"
                 "• Срок выполнения любой работы: 24 часа с момента оплаты.\n"
                 "• Как только работа будет выполнена, я пришлю вам итоговый файл.\n\n"
                 "Если у вас возникнут вопросы, вы можете обратиться в техническую поддержку.", 
                 reply_markup=markup)

# Обработчик сообщений поддержки
def handle_support(message):
    if message.text and message.text.startswith('/'):
        if message.text == '/support':
            return support(message)
        elif message.text == '/new_task':
            return new_task(message)
        return
        
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    new_task_btn = types.KeyboardButton('Новое задание')
    support_btn = types.KeyboardButton('Поддержка')
    markup.row(new_task_btn, support_btn)
    
    bot.reply_to(message, 
                 "Спасибо за обращение!\n"
                 "Я рассмотрю ваш вопрос и отвечу в ближайшее время.",
                 reply_markup=markup)

# Обработчик команды /support
@bot.message_handler(commands=['support'])
def support(message):
    markup = types.ReplyKeyboardRemove()
    bot.send_message(message.chat.id, 
                     "Пожалуйста, опишите вашу проблему:\n"
                     "- Проблема с выполненным заданием\n"
                     "- Технические проблемы с ботом\n"
                     "- Другие вопросы",
                     reply_markup=markup)
    bot.register_next_step_handler(message, handle_support)

# Обработчик команды /new_task
@bot.message_handler(commands=['new_task'])
def new_task(message):
    send_welcome(message)

# Запуск бота
if __name__ == "__main__":
    set_commands()
    while True:
        try:
            logger.info("Запуск бота...")
            bot.polling(none_stop=True, interval=1, timeout=60)
        except Exception as e:
            logger.error(f"Ошибка подключения к Telegram: {e}")
            time.sleep(10)