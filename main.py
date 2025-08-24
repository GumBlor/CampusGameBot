import telebot
from telebot import types
import sqlite3

'''
ИДЕЯ БОТА.

1. Регистрация каждого человека. Предлагается несколько (сколько?) вопросов из базы данных,
сохранение ответов на них в другой (!) базе данных (капсом, слитно). Указывается ФИО. Загрузка
собственной фотографии/описания (возможность менять их?). Также при старте генерируется описание бота и правила игры.

2. Кнопка, с помощью которой можно редактировать свой ответ.

3. Кнопка, которая генерирует вам человека, выдает его фото и вопрос(ы). Нельзя генерировать нового, пока не нашел старого. Сохранение в БД
ID всех угаданных людей - фактически количество очков. Новый человек генерируется после сверки со всеми угаданными ID,
чтобы избежать повторения в генерации человека. При генерации также проводится проверка на факт того, что мы не выпали человеку,
который выпал нам - чтобы была замкнутая цепь. Сразу пишет вопрос из базы данных, после отгадывания - следующий. 

4. Кнопка, которая показывает рейтинг (?)

БАЗА ДАННЫХ.
* ID
* Вопросы
* Ответы
* Угаданные ID
* Занят / не занят
* Фотография / описание
'''

# Идентификатор бота, генерируется у BotFather
bot = telebot.TeleBot('6447415648:AAHAZrEnHgt7Vtlq8aaptxLuGUd4ZlQCLig')

# Метод, выполняемый при запуске бота
@bot.message_handler(commands=["start"])
def start(message):
    # Создание кнопки
    # keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    # keyboard.add(types.KeyboardButton(text="Отправить местоположение", request_location=True))

    # Создание базы данных
    db = sqlite3.connect('Data.dat')
    cur = db.cursor()
    # Работает ли boolean?
    cur.execute('''CREATE TABLE IF NOT EXISTS users (
        userID text UNIQUE,
        name text, 
        question text,
        answer text,
        guessedRight text, 
        busyness boolean,
        description text
        )''')
    db.commit()
    cur.close()
    db.close()

    # Отправка описания и правил игры при запуске
    bot.send_message(message.chat.id, "Описание игры.")

    # Присваивание данному ID в БД своих вопросов
    '''
    Реализовать!
    1. Подключение ко второй базе данных
    2. Генерация n (по количеству вопросов) случайных чисел от 1 до кол-ва вопросов в БД (rowid)
    3. Внесение данных вопросов в БД
    '''

    question = ""

    # Добавление в БД вопроса
    conn = sqlite3.connect('Data.dat')
    cur = conn.cursor()
    cur.execute("INSERT OR REPLACE INTO users (question) VALUES ('%s')" % question)
    conn.commit()
    cur.close()
    conn.close()

    # Регистрация
    bot.register_next_step_handler(message, registration)

@bot.message_handler(commands=["registration"])
def registration(message):
    bot.send_message(message.chat.id, "Введите имя")
    bot.register_next_step_handler(message, name)

def name(message):
    # Добавление в БД имени и id пользователя
    db = sqlite3.connect('Data.dat')
    cur = db.cursor()
    cur.execute("INSERT OR REPLACE INTO users (userID, name) VALUES ('%s', '%s')" % (message.from_user.id, message.text))
    db.commit()
    cur.close()
    db.close()

    # Ввод описания (вставка фото)
    bot.send_message(message.chat.id, "Теперь опишите себя (вставьте фото)")
    bot.register_next_step_handler(message, description)

def description(message):
    # Добавление в БД описание (фото) данному ID
    db = sqlite3.connect('Data.dat')
    cur = db.cursor()
    cur.execute("INSERT OR REPLACE INTO users (description) VALUES ('%s')" % message.text)

    # Сохранить ответ из БД, который может отсутствовать
    cur.execute("SELECT answer FROM articles WHERE userID = ('%s')" % message.from_user.id)
    userAnswer = cur.fetchall()

    db.commit()
    cur.close()
    db.close()

    # Вывести поздравление об успешной регистрации
    bot.send_message(message.chat.id, f'Приятно познакомиться!')

    # Если у пользователя нет ответа на вопрос в БД, то написать вопрос и считать ответ,
    # чтобы не менять вопрос при перерегистрации
    ''' None или пустой список, если нет ответа? '''
    if userAnswer is None:
        # Написать вопрос из БД пользователю
        db = sqlite3.connect('Data.dat')
        cur = db.cursor()
        cur.execute("SELECT question FROM articles WHERE userID = ('%s')" % message.from_user.id)
        bot.send_message(message.chat.id, cur.fetchall())
        cur.close()
        db.close()

        bot.register_next_step_handler(message, yourAnswer)

# Изменить в БД ответы на вопросы данного пользователя
@bot.message_handler(commands=["answers"])
def yourAnswer(message):
    db = sqlite3.connect('Data.dat')
    cur = db.cursor()
    # Добавление ответа в соответствующую ячейку
    cur.execute("INSERT OR REPLACE INTO users (answer) VALUES ('%s')" % message.text.upper())
    db.commit()
    cur.close()
    db.close()
    # Просто так
    bot.send_message(message.chat.id, 'Просто прекрасно!')

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


bot.polling(non_stop=True)