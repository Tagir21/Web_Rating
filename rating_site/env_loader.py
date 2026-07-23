from dotenv import load_dotenv
from pathlib import Path

import os

PROJECT_DIR = Path(__file__).resolve().parents[1]
load_dotenv(dotenv_path=PROJECT_DIR / '.env')

def get_env(name: str, default: str | None=None, *, required: bool = False) -> str:
    value = os.getenv(name, default)

    if required and (value is None or value == ''):
        raise RuntimeError(f'Переменная окружения {value} не задана')

    return value or ""


token = get_env('BOT_TOKEN')
admin_id = int(get_env('ADMIN_ID'))

db_hostname = get_env('DB_HOSTNAME', 'localhost', required=False)
db_port = get_env('DB_PORT', '3306', required=False)
db_username = get_env('DB_USERNAME')
db_password = get_env('DB_PASSWORD')
db_name = get_env('DB_NAME')

secret_key = get_env('SECRET_KEY')

public_api_base_url = get_env('PUBLIC_API_BASE_URL', 'http://localhost:8000', required=False).rstrip('/')
internal_api_base_url = get_env('PUBLIC_API_BASE_URL', 'http://localhost:8000', required=False).rstrip('/')

api_base_url = public_api_base_url
proxy_url = get_env('PROXY_URL', "", required=False) or None

cors_origins = [
    origin.strip()
    for origin in get_env('CORS_ORIGINS', ("http://127.0.0.1:8001,http://localhost:8001"), required=False).split(',')
    if origin.strip()
]