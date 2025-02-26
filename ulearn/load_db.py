import csv

import psycopg2

DB_CONFIG = {
    "dbname": "ulearn",
    "user": "postgres",
    "password": "postgres",
    "host": "localhost",
    "port": "5432"
}

try:
    with open('back_csv.csv', 'r') as file:
        reader = csv.reader(file)
        headers = next(reader)
        with psycopg2.connect(**DB_CONFIG) as conn:
            with conn.cursor() as cur:
                for row1 in reader:
                    row = [i if i != '' else None for i in row1]
                    if row[1]:
                        row[1] = row[1].replace('\n', ', ')
                    cur.execute("INSERT INTO ulearn_vacancies (name, key_skills, salary_from, salary_to, salary_currency, area_name, published_at) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                                (row[0], row[1], row[2], row[3], row[4], row[5], row[6]))
                    conn.commit()
                    print("Пользователь добавлен!")

                cur.execute(
                    "INSERT INTO ulearn_statistics (name, data) VALUES (%s, %s)",
                    ("avg_salary_by_city", '{}'))

except psycopg2.Error as e:
    print("Ошибка:", e)