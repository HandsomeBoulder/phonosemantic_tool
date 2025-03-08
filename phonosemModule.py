import sqlite3
import os
from misc import *
import spacy

def main():
    """
    That is a function
    """
    # Перебираем файлы в директории
    paths = pathfinder()
    database = paths["database"]
    if not database:
        print("Database not found")
        exit()

    # Обрабатываем входящий запрос
    while True:
        request = input('Input a verb or a sentence: ').strip()
        if not request:
            print('Empty input')
        elif request.isnumeric():
            print('Input cannot be a number')
        else:
            break

    # NLQ сегмент spaCy
    nlp = spacy.load("en_core_web_trf")  # тяжеловесная CPU модель для английского языка
    sentence, verbs, verb_flag = nlp(request), [], False
    # Находим глаголы
    for token in sentence:
        # Лемматизируем
        if token.pos_ == 'VERB':
            verb_flag = True
            verbs.append(token.lemma_)
    # Обработка исключений
    if verb_flag != True:
        print('No verbs found in input string')
        exit()

    # Устанавливаем соединение с датабазой
    conn = sqlite3.connect(database)
    conn.row_factory = sqlite3.Row   # Возвращаем словарь
    cursor = conn.cursor()
    # Достаем информацию из датабазы
    for verb in verbs:
        cursor.execute("""
            SELECT verbs.verb, verbs.transcription, 
                GROUP_CONCAT(translations.word, ', ') AS translations,
                GROUP_CONCAT(translations.transcription, ', ') AS transcriptions
            FROM verbs
            JOIN translations ON verbs.id = translations.parentId
            WHERE verbs.verb = ?
            GROUP BY verbs.id;
        """, (verb,))
        results = dict(cursor.fetchone())
        # Проверки на вхождение в ДБ
        # if results


    conn.close()
    print(results)

if __name__ == '__main__':
    main()

# лемматизировать поступивший на вход глагол, чтобы искать в датабазе словарную форму, а не прошедш. время
# Можно получать на вход целое предложение и автоматически искать в нем глаголы
# Использовать расстояние Левенштейна, чем оно лучше, тем больше подходит эквивалент
# Показывать рейтинг глаголов по фоносемантической близости