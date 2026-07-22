from dotenv import dotenv_values
from pathlib import Path

ENV_DIR = Path(__file__).resolve().parent / '.env'
config = dotenv_values(ENV_DIR)

token = config['BOT_TOKEN']
admin_id = config['ADMIN_ID']

db_hostname = config['DB_HOSTNAME']
db_port = config['DB_PORT']
db_username = config['DB_USERNAME']
db_password = config['DB_PASSWORD']
db_name = config['DB_NAME']

secret_key = config['SECRET_KEY']

api_base_url = config['API_BASE_URL']
proxy_url = config['PROXY_URL']