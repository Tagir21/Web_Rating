from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from db_conn import get_all_grades

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8001"],
    allow_methods=["GET"]
)

@app.get('/get_all_akademy_grades')
async def get_all_akademy_grades():
    all_akademy_grades = await get_all_grades()
    print("Я работаю, всё ок")
    return {'grades': all_akademy_grades}