import telebot
from telebot import types
import logging
import time

# Настройка базового логирования для отслеживания работы бота
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

#-------------------- ОСНОВНЫЕ НАСТРОЙКИ --------------------#

# Токен бота, полученный от BotFather
bot = telebot.TeleBot('7582178055:AAGRAXRJQeLDgIiSF_B7Ui0hm596HhXnuNM')

# ID чата администратора для получения заявок
ADMIN_CHAT_ID = "YOUR_ADMIN_CHAT_ID"

#-------------------- НАСТРОЙКА КОМАНД БОТА --------------------#

def set_commands():
    """Установка основных команд бота, отображаемых в меню"""
    commands = [
        types.BotCommand("start", "Начать работу с ботом"),
        types.BotCommand("support", "Написать в техническую поддержку"),
        types.BotCommand("new_task", "Выполнить новое задание")
    ]
    bot.set_my_commands(commands)

#-------------------- ОБРАБОТЧИКИ КОМАНД --------------------#

@bot.message_handler(commands=['start'])
def send_welcome(message):
    """
    Обработчик команды /start
    Отправляет приветственное сообщение и показывает главное меню с предметами
    """
    # Создание клавиатуры с предметами
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = [
        ['ДПП', 'Базы Данных'],
        ['Архитектурное Моделирование'],
        ['Кастомная работа']
    ]
    for row in buttons:
        markup.row(*[types.KeyboardButton(btn) for btn in row])

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

#-------------------- ОБРАБОТКА ВЫБОРА ПРЕДМЕТА --------------------#

@bot.message_handler(content_types=['text'])
def handle_subject_selection(message):
    """
    Обработчик текстовых сообщений
    Обрабатывает выбор предмета и перенаправляет на соответствующие действия
    """
    try:
        # Игнорируем команды
        if message.text.startswith('/'): 
            return
        
        # Обработка кнопок меню
        if message.text == 'Новое задание':
            return new_task(message)
        elif message.text == 'Поддержка':
            return support(message)
        
        # Обработка выбора предмета
        valid_subjects = ['ДПП', 'Базы Данных', 'Архитектурное Моделирование', 'Кастомная работа']
        if message.text in valid_subjects:
            # Убираем клавиатуру и запрашиваем детали задания
            markup = types.ReplyKeyboardRemove()
            instruction_text = f"""Вы выбрали предмет: {message.text}

Пожалуйста, опишите задание подробно:
- Полное название задания
- Ссылка на задание на Moodle
- ФИО, академическая группа, номер студенческого билета
- Сроки выполнения
- Дополнительные требования"""
            
            bot.send_message(message.chat.id, instruction_text, reply_markup=markup)
            bot.register_next_step_handler(message, get_task_details)
            
    except Exception as e:
        logger.error(f"Ошибка в handle_subject_selection: {e}")
        bot.reply_to(message, "Произошла ошибка. Пожалуйста, попробуйте еще раз или обратитесь в поддержку.")

#-------------------- АДМИНИСТРАТИВНЫЕ ФУНКЦИИ --------------------#

def create_admin_keyboard(task_id, user_id):
    """Создание клавиатуры для администратора с кнопками управления заказом"""
    markup = types.InlineKeyboardMarkup()
    markup.row(
        types.InlineKeyboardButton("Начать работу", callback_data=f"start_{task_id}_{user_id}"),
        types.InlineKeyboardButton("Оплата получена", callback_data=f"paid_{task_id}_{user_id}")
    )
    markup.row(
        types.InlineKeyboardButton("Отправить результат", callback_data=f"complete_{task_id}_{user_id}")
    )
    return markup

#-------------------- ОБРАБОТКА ДЕТАЛЕЙ ЗАДАНИЯ --------------------#

def get_task_details(message):
    """
    Обработчик получения деталей задания от пользователя
    Отправляет информацию администратору и подтверждение пользователю
    """
    # Проверка на команды
    if message.text and message.text.startswith('/'):
        if message.text == '/support':
            return support(message)
        elif message.text == '/new_task':
            return new_task(message)
        return

    # Генерация уникального ID задания на основе времени
    task_id = str(int(time.time()))
    
    # Формирование сообщения для администратора
    admin_text = f"""Новая заявка #{task_id}
От: @{message.from_user.username}
ID пользователя: {message.from_user.id}

Предмет: {message.text}
Детали задания:
{message.text}"""
    
    # Отправка заявки администратору с кнопками управления
    markup = create_admin_keyboard(task_id, message.from_user.id)
    bot.send_message(ADMIN_CHAT_ID, admin_text, reply_markup=markup)

    # Создание клавиатуры для пользователя
    markup_user = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup_user.row(
        types.KeyboardButton('Новое задание'),
        types.KeyboardButton('Поддержка')
    )
    
    # Отправка подтверждения пользователю
    bot.reply_to(message, 
                 "Спасибо за предоставленную информацию!\n"
                 "Заявка принята!\n\n"
                 "После утверждения заявки я пришлю вам уведомление.",
                 reply_markup=markup_user)

#-------------------- СИСТЕМА ПОДДЕРЖКИ --------------------#

def handle_support(message):
    """
    Обработчик сообщений технической поддержки
    Принимает вопросы пользователей и отправляет подтверждение
    """
    # Проверка на команды
    if message.text and message.text.startswith('/'):
        if message.text == '/support':
            return support(message)
        elif message.text == '/new_task':
            return new_task(message)
        return
        
    # Создание стандартной клавиатуры
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(
        types.KeyboardButton('Новое задание'),
        types.KeyboardButton('Поддержка')
    )
    
    bot.reply_to(message, 
                 "Спасибо за обращение!\n"
                 "Я рассмотрю ваш вопрос и отвечу в ближайшее время.",
                 reply_markup=markup)

@bot.message_handler(commands=['support'])
def support(message):
    """Обработчик команды /support - начало диалога с поддержкой"""
    markup = types.ReplyKeyboardRemove()
    bot.send_message(message.chat.id, 
                     "Пожалуйста, опишите вашу проблему:\n"
                     "- Проблема с выполненным заданием\n"
                     "- Технические проблемы с ботом\n"
                     "- Другие вопросы",
                     reply_markup=markup)
    bot.register_next_step_handler(message, handle_support)

@bot.message_handler(commands=['new_task'])
def new_task(message):
    """Обработчик команды /new_task - перезапуск процесса создания задания"""
    send_welcome(message)

#-------------------- ОБРАБОТКА CALLBACK ЗАПРОСОВ --------------------#

@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    """
    Обработчик нажатий на инлайн-кнопки администратора
    Управляет статусом заказа и отправляет уведомления пользователю
    """
    action, task_id, user_id = call.data.split('_')
    
    if action == "start":
        # Отправка информации об оплате
        payment_info = """Заявка подтверждена!

Для оплаты работы (1000 рублей) используйте следующие реквизиты:
ТБанк: 1111 2222 3333 4444
TON: 11111111111111111111111111111111
SOL: 11111111111111111111111111111111"""
        
        bot.send_message(user_id, payment_info)
        bot.answer_callback_query(call.id, "Уведомление об оплате отправлено")
        
    elif action == "paid":
        # Подтверждение получения оплаты
        bot.send_message(user_id, 
                        "Оплата получена! Ваша работа взята в работу.\n"
                        "Срок выполнения: 24 часа.")
        bot.answer_callback_query(call.id, "Уведомление об успешной оплате отправлено")
        
    elif action == "complete":
        # Завершение работы и запрос файла решения
        bot.send_message(user_id, 
                        "Ваша работа выполнена! Файл с решением будет отправлен следующим сообщением.")
        bot.answer_callback_query(call.id, "Уведомление о завершении отправлено")
        
        bot.send_message(call.message.chat.id, "Пожалуйста, отправьте файл с решением.")
        bot.register_next_step_handler(call.message, send_solution_file, user_id)

#-------------------- ОТПРАВКА ФАЙЛОВ --------------------#

def send_solution_file(message, user_id):
    """
    Обработчик отправки файла решения
    Проверяет корректность отправленного файла и пересылает его пользователю
    """
    try:
        if not message.document:
            bot.reply_to(message, "Пожалуйста, отправьте файл.")
            bot.register_next_step_handler(message, send_solution_file, user_id)
            return
        
        # Пересылка файла пользователю
        bot.send_document(user_id, message.document.file_id, caption="Вот ваше решение!")
        bot.reply_to(message, "Файл успешно отправлен пользователю!")
        
    except Exception as e:
        logger.error(f"Ошибка при отправке файла: {e}")
        bot.reply_to(message, "Произошла ошибка при отправке файла. Попробуйте еще раз.")
        bot.register_next_step_handler(message, send_solution_file, user_id)

#-------------------- ЗАПУСК БОТА --------------------#

if __name__ == "__main__":
    # Установка команд бота
    set_commands()
    
    # Бесконечный цикл работы бота с обработкой ошибок
    while True:
        try:
            logger.info("Запуск бота...")
            bot.polling(none_stop=True, interval=1, timeout=60)
        except Exception as e:
            logger.error(f"Ошибка подключения к Telegram: {e}")
            # Пауза перед повторным подключением
            time.sleep(10)