import telebot
from telebot import types
import sqlite3
import random

# Идентификатор бота, генерируется у BotFather
bot = telebot.TeleBot('7948416680:AAHYWYLiZOGoZncWqvDXUaIaEjmjbnXW0Ao')

# Метод, выполняемый при запуске бота
@bot.message_handler(commands=["start"])
def start(message):
    # Создание кнопки
    # keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    # keyboard.add(types.KeyboardButton(text="Отправить местоположение", request_location=True))

    # Создание базы данных
    db = sqlite3.connect('Data.db')
    cur = db.cursor()
    # Создание таблицы
    cur.execute('''CREATE TABLE IF NOT EXISTS users (
        userID TEXT UNIQUE,
        name TEXT, 
        question TEXT,
        answer TEXT,
        guessedRight TEXT, 
        busyness INTEGER DEFAULT 0, -- 1 = True, 0 = False
        description TEXT
        )''')
    db.commit()
    cur.close()
    db.close()

    # Отправка описания и правил игры при запуске
    bot.send_message(message.chat.id, "Описание игры.")

    # Присваивание данному ID в БД своих вопросов

    # Подключение к БД с вопросами
    questionDb = sqlite3.connect('Questions.db')
    curQestionDb = questionDb.cursor()

    # Получаем общее количество вопросов
    curQestionDb.execute("SELECT COUNT(*) FROM questions")
    total_questions = curQestionDb.fetchone()[0]

    # Генерируем случайный номер от 1 до количества вопросов
    random_id = random.randint(1, total_questions)

    # Получаем вопрос по случайному ID
    curQestionDb.execute("SELECT * FROM questions WHERE rowid = ?", (random_id,))
    question = curQestionDb.fetchone()[1]

    curQestionDb.close()
    questionDb.close()

    # Добавление в БД вопроса данному пользователю
    conn = sqlite3.connect('Data.db')
    cur = conn.cursor()

    # Добавление ID и вопроса
    cur.execute("INSERT OR REPLACE INTO users (userID, question) VALUES (?, ?)", (message.from_user.id, question))
    conn.commit()
    cur.close()
    conn.close()

    # Регистрация
    registration(message)

@bot.message_handler(commands=["registration"])
def registration(message):
    bot.send_message(message.chat.id, "Введите имя")
    bot.register_next_step_handler(message, name)

def name(message):
    # Добавление в БД имени пользователя
    db = sqlite3.connect('Data.db')
    cur = db.cursor()
    cur.execute(
        "UPDATE users SET name = ? WHERE userID = ?",
        (message.text, message.from_user.id)
    )
    db.commit()
    cur.close()
    db.close()

    # Ввод описания (вставка фото)
    bot.send_message(message.chat.id, "Теперь опишите себя (вставьте фото)")
    bot.register_next_step_handler(message, description)

def description(message):
    # Добавление в БД описание (фото) данному ID
    db = sqlite3.connect('Data.db')
    cur = db.cursor()
    cur.execute(
        "UPDATE users SET description = ? WHERE userID = ?",
        (message.text, message.from_user.id)
    )

    # Сохранить ответ на вопрос из БД (он может отсутствовать)
    cur.execute("SELECT answer FROM users WHERE userID = ?", (message.from_user.id,))
    userAnswer = cur.fetchone()[0]

    db.commit()
    cur.close()
    db.close()


    # Вывод всех зареганных юзеров
    db = sqlite3.connect('Data.db')
    cur = db.cursor()

    cur.execute("SELECT * FROM users")
    usrs = cur.fetchall()
    print(usrs)

    cur.close()
    db.close()


    # Вывести поздравление об успешной регистрации
    bot.send_message(message.chat.id, f'Приятно познакомиться!')

    # Если у пользователя нет ответа на вопрос в БД, то написать вопрос и считать ответ,
    # чтобы не менять вопрос при перерегистрации
    ''' Выводится при повторной регистрации - проблема '''
    if userAnswer is None:
        # Написать вопрос из БД пользователю
        writeQuestion(message)


# Написать вопрос из БД пользователю
@bot.message_handler(commands=["answers"])
def writeQuestion(message):
    db = sqlite3.connect('Data.db')
    cur = db.cursor()
    cur.execute("SELECT question FROM users WHERE userID = ?", (message.from_user.id,))
    db.commit()
    bot.send_message(message.chat.id, cur.fetchone()[0])
    cur.close()
    db.close()

    bot.register_next_step_handler(message, yourAnswer)

# Изменить в БД ответы на вопросы данного пользователя
def yourAnswer(message):
    db = sqlite3.connect('Data.db')
    cur = db.cursor()
    # Добавление ответа в соответствующую ячейку
    cur.execute(
        "UPDATE users SET answer = ? WHERE userID = ?",
        (message.text, message.from_user.id)
    )
    db.commit()
    cur.close()
    db.close()
    # Просто так
    bot.send_message(message.chat.id, 'Просто прекрасно!')

"""

@bot.message_handler(commands=["generate"])
def generate(message):
    '''
    Команда, которая генерирует вам человека, выдает его фото и вопрос(ы). Новый человек генерируется после сверки
    со всеми угаданными ID, чтобы избежать повторения в генерации человека. При генерации также проводится проверка на
    факт того, что мы не выпали человеку, который выпал нам - чтобы была замкнутая цепь.
    '''

    # Нельзя генерировать нового, пока не нашел старого.

    # Если busyness == True, то идти дальше по списку, иначе - выбрать

    question(message)


def question(message):
    ''' Показывает вопрос человека '''
    bot.register_next_step_handler(message, isTrue)

def isTrue(message):
    ''' Если ответ верный, то выводит поздравление и записывает балл в БД, а если нет, то кидает обратно на question() '''
    
"""

bot.polling(non_stop=True)