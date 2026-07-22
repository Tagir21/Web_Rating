from rating_site.tg_bot.db_connection import db_connect

def is_user_register(user_name: str):
    conn, cursor = db_connect()
    cursor.execute('SELECT id, is_banned'
                   ' FROM telegram_data'
                   ' WHERE tg_name = %s', (user_name,))
    user_data = cursor.fetchone()
    conn.close()

    return user_data

def is_valid_login(login: str):
    conn, cursor = db_connect()
    cursor.execute('SELECT id, name FROM users WHERE login = %s', (login,))
    user_id = cursor.fetchone()
    conn.close()

    return user_id

def linked_telegrams(user_id: int):
    conn, cursor = db_connect()
    cursor.execute('SELECT tg_name'
                   ' FROM telegram_data'
                   ' WHERE user_id = %s', (user_id,))
    telegrams = cursor.fetchall()
    conn.close()

    return telegrams

def get_viewing_requests_count():
    conn, cursor = db_connect()
    cursor.execute(
        'SELECT COUNT(*) AS count FROM achievements WHERE status = "viewing"'
    )
    total_count = cursor.fetchone()[0]
    conn.close()

    return total_count

def get_all_viewing_requests():
    conn, cursor = db_connect()
    cursor.execute('SELECT id, (SELECT tg_name FROM telegram_data WHERE telegram_data.id = user_tg_id),'
                   ' category_id, description, file_path, file_type'
                   ' FROM achievements WHERE status = "viewing"')
    all_viewing_requests = cursor.fetchall()
    conn.close()

    return all_viewing_requests