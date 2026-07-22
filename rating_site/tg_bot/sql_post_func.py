from rating_site.tg_bot.db_connection import db_connect
from rating_site.backend.db_get_requests import get_category_data
import json

def add_tg_user_name_in_db(tg_user_name: str, user_id: int):
    conn, cursor = db_connect()
    cursor.execute('INSERT INTO telegram_data (user_id, tg_name)'
                   ' VALUES'
                   ' (%s, %s)', (user_id, tg_user_name))
    conn.commit()
    conn.close()

async def update_request(request_id, status, category=None, grade=None):
    conn, cursor = db_connect()

    if grade and category:
        category_data_map = await get_category_data()
        category_id = (category_data_map.get(category))['id']

        cursor.execute('UPDATE achievements SET status = %s, category_id = %s, grade = %s WHERE id = %s',
                       (status, json.dumps([category_id]), grade, request_id))
    else:
        cursor.execute('UPDATE achievements SET status = %s WHERE id = %s',
                       (status, request_id))
    conn.commit()
    conn.close()


def ban_user_by_tg_user_name(request_id):
    conn, cursor = db_connect()
    cursor.execute('UPDATE telegram_data'
                   ' SET is_banned = 1'
                   ' WHERE id = (SELECT user_tg_id'
                   '             FROM achievements'
                   '             WHERE id = %s)', (request_id,))
    conn.commit()
    conn.close()