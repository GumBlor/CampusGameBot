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
        guessedRight TEXT DEFAULT '', -- list угаданных пользователей
        busyness TEXT DEFAULT 'free', -- *userID* = пользователь кем-то занят, free = пользователь свободен
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

    # Вывести поздравление об успешной регистрации
    bot.send_message(message.chat.id, f'Приятно познакомиться!')

    # Если у пользователя нет ответа на вопрос в БД, то написать вопрос и считать ответ,
    # чтобы не менять вопрос при перерегистрации
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


@bot.message_handler(commands=["generate"])
def generate(message):
    '''
    1. Получить список всех юзеров.
    2. Проверка: если у кого-то в busyness есть наш ID, то написать пользователю, что он уже кого-то ищет.
    Если же ни у кого нет нашего ID, то выполнять код.
    3. Пройтись по нему, смотря параметр busyness. Если он = 0, то смотрится,
    не совпадает ли наше значение busyness с его ID (иными словами, не отгадывает ли он нас в данный момент).
    4. Если пользователь не отгадывает нас, то смотрится, не отгадывал ли он нас до этого
    5. Если пользователь не отгадывал нас до этого, то смотрится, не отгадывали ли мы его до этого
    6. Если не отгадывали, то обновить busyness пользователя на наш ID. Вывести вопрос данного человека
    '''

    # Вывод всех зарегистрированных юзеров
    db = sqlite3.connect('Data.db')
    cur = db.cursor()

    cur.execute("SELECT * FROM users")
    usrs = cur.fetchall()

    # Получить информацию о себе
    I = usrs[0]
    IamBusy = False
    for usr in usrs:
        if usr[0] == message.from_user.id:
            I = usr
        if usr[5] == I[0]:
            IamBusy = True

    cur.close()
    db.close()

    # Если у некоторого пользователя в busyness есть наш ID, то написать нам, что мы уже кого-то ищем.
    # Если же ни у кого нет нашего ID, то выполнять код.
    if IamBusy:
        bot.send_message(message.chat.id, 'Да вам бы старого отгадать!')
    else:
        for usr in usrs:
            # Пользователь свободен, а также это не я
            if (usr[5] == 'free') and (usr[0] != I[0]):
                # Проверка, не отгадывает ли он нас в данный момент
                if I[5] != usr[0]:
                    # Смотрится, не отгадывал ли он нас до этого
                    if (usr[4] is None) or (I[0] in usr[4].split()):
                        # Смотрится, не отгадывали ли мы его до этого
                        if (I[4] is None) or (usr[0] in I[4].split()):
                            # Обновить busyness пользователя на наш ID
                            db = sqlite3.connect('Data.db')
                            cur = db.cursor()
                            cur.execute(
                                "UPDATE users SET busyness = ? WHERE userID = ?",
                                (I[0], usr[0])
                            )
                            db.commit()
                            cur.close()
                            db.close()
                            # Вывести вопрос данного человека
                            info(message, usr)


def info(message, usr):
    # Вывести описание (фото)
    bot.send_message(message.chat.id, usr[6])
    # Вывести вопрос
    bot.send_message(message.chat.id, usr[2])

    bot.register_next_step_handler(message, isTrue, usr)

def isTrue(message, usr):
    if message.text == usr[3]:
        db = sqlite3.connect('Data.db')
        cur = db.cursor()

        # Записать в БД значение угаданного ID
        cur.execute(
            "UPDATE users SET guessedRight = guessedRight || ' ' || ? WHERE userID = ?",
            (usr[0], message.from_user.id)
        )
        # Обнулить busyness пользователя, за которым мы охотились
        cur.execute(
            "UPDATE users SET busyness = 'free' WHERE userID = ?",
            (usr[0],)
        )
        db.commit()
        cur.close()
        db.close()

        bot.send_message(message.chat.id, 'Ответ верный!')
    else:
        bot.send_message(message.chat.id, 'Ответ не верный!')
        info(message, usr)

# Показывает рейтиг
@bot.message_handler(commands=["rating"])
def rating(message):
    ''' Считает баллы всех в списке, показывает топ 5 людей (их имена и баллы) '''

bot.polling(non_stop=True)