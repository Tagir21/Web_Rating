from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from db_conn import get_all_users

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:8001"],
    allow_methods=["GET"]
)

@app.get('/get_api_all_users')
async def get_all_api_users():
    all_users = await get_all_users()
    print("Я работаю, всё ок")
    return {'users': all_users}