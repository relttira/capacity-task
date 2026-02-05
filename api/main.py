from datetime import date

from fastapi import FastAPI


app = FastAPI()

@app.get('/capacity/')
def get_capacity(date_from: date, date_to: date) -> int:
    return 0
