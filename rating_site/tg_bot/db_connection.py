from mysql.connector import connect
from rating_site.env_loader import (
    db_hostname,
    db_port,
    db_username,
    db_password,
    db_name,
)

def db_connect():
    conn = connect(host=db_hostname,
                   port=db_port,
                   username=db_username,
                   password=db_password,
                   database=db_name)
    cursor = conn.cursor()

    return conn, cursor