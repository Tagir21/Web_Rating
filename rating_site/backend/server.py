from fastapi import FastAPI

from db_conn import get_all_grades

app = FastAPI()

@app.get('/get_all_akademy_grades')
async def get_all_akademy_grades():
    all_akademy_grades = await get_all_grades()

    return {'grades': all_akademy_grades}