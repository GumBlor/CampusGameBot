import sqlite3
import random


# Создание базы данных и таблицы с вопросами

conn = sqlite3.connect('Questions.db')
cursor = conn.cursor()

# Создаем таблицу вопросов
cursor.execute('''
    CREATE TABLE IF NOT EXISTS questions (
        question_text TEXT NOT NULL
    )''')

conn.commit()

# Добавление заранее подготовленных вопросов в базу данных

cursor = conn.cursor()

# Примеры вопросов (можно заменить на свои)
questions_list = [
    "Что такое Python?",
    "Сколько планет в Солнечной системе?",
    "Кто написал 'Войну и мир'?",
    "Что такое фотосинтез?",
    "Столица Франции?",
    "Что такое ООП?"
    ]
# Преобразуем список в список кортежей с одним элементом
questions_tuples = [(question,) for question in questions_list]

# Вставляем вопросы в базу
for item in questions_tuples:
    cursor.execute(
        "INSERT INTO questions (question_text) VALUES (?)", item
    )

conn.commit()
print(f"Добавлено {len(questions_tuples)} вопросов в базу данных")

conn.close()

'''
def get_random_question(conn):
    """Получение случайного вопроса из базы данных"""
    cursor = conn.cursor()

    # Получаем общее количество вопросов
    cursor.execute("SELECT COUNT(*) FROM questions")
    total_questions = cursor.fetchone()[0]

    if total_questions == 0:
        print("В базе данных нет вопросов!")
        return None

    # Генерируем случайный номер от 1 до количества вопросов
    random_id = random.randint(1, total_questions)

    # Получаем вопрос по случайному ID
    cursor.execute("SELECT * FROM questions WHERE id = ?", (random_id,))
    question = cursor.fetchone()

    return question
'''
