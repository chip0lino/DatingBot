import sqlite3

conn = sqlite3.connect('database.db')
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        name TEXT,
        gender TEXT,
        age INTEGER,
        photo TEXT,
        anketa_description TEXT,
        zodiac_sign TEXT,
        kurs INTEGER,
        faculty TEXT,
        grade INTEGER
    )
''')

conn.commit()