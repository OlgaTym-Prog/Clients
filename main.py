import psycopg2


# Функция для создания базы данных

def create_db(conn):
    with conn.cursor() as cur:
        cur.execute("""
            DROP TABLE IF EXISTS phones;
            DROP TABLE IF EXISTS clients;
        """)

        # Таблица для хранения информации о клиентах
        cur.execute("""
            CREATE TABLE IF NOT EXISTS clients (
                 id SERIAL PRIMARY KEY,
                first_name VARCHAR(50)  NOT NULL,
                 last_name VARCHAR(50)  NOT NULL,
                     email VARCHAR(100) NOT NULL 
            );
        """)

        # Таблица для хранения информации о телефонах клиентов
        cur.execute("""
            CREATE TABLE IF NOT EXISTS phones (
                id SERIAL PRIMARY KEY,
                client_id INTEGER REFERENCES clients(id) ON DELETE CASCADE,
                    phone VARCHAR(20) 
            );
        """)

        conn.commit()


# Функция для добавления нового клиента

def add_client(conn, first_name, last_name, email, phones=None):
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO clients (first_name, last_name, email)
            VALUES (%s, %s, %s)
            RETURNING id;
        """, (first_name, last_name, email))
        client_id = cur.fetchone()[0]

        if phones:
            for phone in phones:
                cur.execute("""
                    INSERT INTO phones (client_id, phone)
                    VALUES (%s, %s)
                """, (client_id, phone))

        conn.commit()


# Функция для добавления телефона длдя существующего клиента

def add_phone(conn, client_id, phone):
    with conn.cursor() as cur:
        cur.execute("""
           INSERT INTO phones (client_id, phone)
           VALUES (%s, %s);
        """, (client_id, phone))

        conn.commit()


#  Функция для изменения данных о клиенте

def change_client(conn, client_id, first_name=None, last_name=None, email=None, phones=None):
    with conn.cursor() as cur:
        if first_name or last_name or email:
            cur.execute("""
                UPDATE clients
                   SET first_name = COALESCE(%s, first_name),
                        last_name = COALESCE(%s, last_name),
                            email = COALESCE(%s, email)
                 WHERE id = %s;
            """, (first_name, last_name, email, client_id))

        if phones:
            cur.execute("""
                DELETE FROM phones
                 WHERE client_id = %s;
            """, (client_id, ))

            for phone in phones:
                cur.execute("""
                    INSERT INTO phones (client_id, phone)
                    VALUES (%s, %s)
                """, (client_id, phone))

        conn.commit()


# Функция для удаления телефона для существующего клиента

def delete_phone(conn, client_id, phone):
    with conn.cursor() as cur:
        cur.execute("""
            DELETE FROM phones
             WHERE client_id = %s AND phone = %s;
        """, (client_id, phone))

        conn.commit()


# Функция для удаления существующего клиента

def delete_client(conn, client_id):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT COUNT(*) FROM clients
             WHERE id = %s;
        """, (client_id, ))

        if cur.fetchone()[0] > 0:
            cur.execute("""
                DELETE FROM clients 
                 WHERE id = %s;
            """, (client_id,))

            conn.commit()
        else:
            print("Такого клиента нет в базе данных")


# Функция для поиска клиента по имени, фамилии, email или телефону

def find_client(conn, first_name=None, last_name=None, email=None, phone=None):
    with conn.cursor() as cur:
        query = """
            SELECT clients.id, first_name, last_name, email, phone
              FROM clients
              LEFT JOIN phones
                ON clients.id = phones.client_id
             WHERE TRUE
        """

        params = []
        if first_name:
            query += " AND first_name = %s"
            params.append(first_name)

        if last_name:
            query += " AND last_name = %s"
            params.append(last_name)

        if email:
            query += " AND email = %s"
            params.append(email)

        if phone:
            query += " AND phone = %s"
            params.append(phone)

        cur.execute(query, tuple(params))
        return cur.fetchall()


# Пример использования функций

if __name__ == "__main__":
    with psycopg2.connect(database="clients_db", user="postgres", password="frida2809") as conn:
        create_db(conn)

        # Добавление нового клиента

        add_client(conn, "Василий", "Тёркин", "terkin23@mail.ru", phones=["+7 992 345 99 99", "+7 990 888 88 88"])
        add_client(conn, "Пётр", "Первый", "pervyi456@mail.ru", phones=["+7 990 888 88 56"])

        # Добавление телефона для существующего клиента

        add_phone(conn, 1, "+7 999 098 99 99")

        # Изменение данных о клиенте

        change_client(conn, 2, first_name="Олег", phones=["+7 999 999 99 99"])

        # Удаляем клиента

        delete_client(conn, 2)

        # Поиск клиента по имени

        clients = find_client(conn, first_name="Василий")
        for client in clients:
            print(client)

    conn.close()
