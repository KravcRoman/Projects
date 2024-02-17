import psycopg2

try:
    # Подключение к БД
    connection = psycopg2.connect(dbname="app", host="81.90.180.198", user="app", password="pH7sJ5tJ7omT7b", port="5432")

    # Получаем данные по конкретной стадии из БД
    with connection.cursor() as cursor:
        cursor.execute(
            """SELECT 
                stage_name, count(*) 
            FROM 
                public.yucrm2 
            WHERE 
                stage_name = 'Эксклюзивный договор заключен'
            GROUP BY
               "stage_name" ORDER BY "stage_name";"""
        )
        print(*(cursor.fetchone()))

    # Получаем общее кол-во лидов
    with connection.cursor() as cursor1:
        cursor1.execute(
            """SELECT 
                count(*) 
            FROM 
                public.yucrm2 
            GROUP BY
               "stage_name" ORDER BY "stage_name";"""
        )
        print(*(cursor1.fetchone()))

    # Получаем данные по всем отделам
    with connection.cursor() as cursor2:
        cursor2.execute(
            """SELECT 
                department_name 
            FROM 
                public.yucrm
            GROUP BY
               "department_name" ORDER BY "department_name";"""
        )
        print(*(cursor2.fetchall()))

except Exception as _ex:
    print("[INFO] Error while working with PostgreSQL", _ex)
finally:
    if connection:
        connection.close()
        print("[INFO] PostgreSQL connection closed")