import pandas as pd
import os
import sqlite3
from misc import *


def main() -> None:
    """
    This is a function that parses csv table and inserts its values into sqlite3 database
    """
    # Проверяем файлы
    paths = pathfinder()
    excel_table, database = paths["csv_table"], paths["database"]
    # Проверяем наличие таблицы
    if not excel_table:
        print("Csv table is not detected. Exiting...")
        exit()
    # Проверяем наличие ДБ
    if database:
        while True:
            response = input('Database already exists, delete? (y/n) ').strip().lower()
            if response == 'y':
                os.remove(database)
                print('Old database deleted')
                break
            elif response == 'n':
                print('Exiting...')
                exit()
            else:
                print('Invalid input. Try again')

    print("Compiling database...")

    # Подключаемся к ДБ
    conn = sqlite3.connect("phonosemantic.db")
    cursor = conn.cursor()

    # Создаем таблицу для глаголов
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS verbs (
    id INTEGER PRIMARY KEY,
    verb TEXT NOT NULL,
    transcription TEXT NOT NULL,
    category TEXT NOT NULL,
    meaning TEXT NOT NULL
    )
    ''')

    # Создаем таблицу для переводов
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS translations (
    id INTEGER PRIMARY KEY,
    parentId INTEGER NOT NULL,
    word TEXT NOT NULL,
    transcription TEXT NOT NULL,
    FOREIGN KEY (parentId) REFERENCES verbs(id) ON DELETE CASCADE
    )
    ''')

    # Применяем изменения
    conn.commit()

    # Читаем файл
    df = pd.read_csv(excel_table)
    df.dropna(inplace = True)
    for row in df.itertuples():
        # Вносим данные в таблицу глаголов
        word, category, meaning = row.verb.strip(), row.category.strip(), row.meaning.strip()
        transcriptionEn = row.transcriptionEn.replace('/', '').replace('.', '').strip()
        cursor.execute("INSERT INTO verbs (verb, transcription, category, meaning) VALUES (?, ?, ?, ?)", 
                        (word, transcriptionEn, category, meaning))
        # Вносим данные в таблицу переводов
        parent = cursor.lastrowid
        translations = row.translation.split(',')
        transcriptionsRu = row.transcriptionRu.split(',')
        for translation, transcriptionRu in zip(translations, transcriptionsRu):
            translation, transcriptionRu = translation.strip().lower(), transcriptionRu.replace('/', '').replace('.', '').strip()
            cursor.execute("INSERT INTO translations (parentId, word, transcription) VALUES (?, ?, ?)", 
                            (parent, translation, transcriptionRu))

    # Применяем изменения и закрываем подключение к ДБ
    conn.commit()
    conn.close()

    print(f'Database successfully compiled with {parent} verbs total')

if __name__ == '__main__':
    main()