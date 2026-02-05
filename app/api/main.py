from datetime import date

from fastapi import FastAPI
from sqlalchemy.engine.cursor import CursorResult

from app.api.models.WeeklyCapacity import WeeklyCapacity
from app.database.SQLiteHandler import SQLiteHandler
from app.database.queries.capacity import CAPACITY


app = FastAPI()

@app.on_event('startup')    # TODO: Use lifespan event handlers.
def on_startup():
    SQLiteHandler.init_database()

@app.get('/capacity')
def get_capacity(session: SQLiteHandler.SessionDep, date_from: date, date_to: date) -> list[WeeklyCapacity]:   # TODO: Add constraints?
    params = {'date_from': date_from, 'date_to': date_to}
    result: CursorResult = session.exec(statement=CAPACITY, params=params)
    return [WeeklyCapacity(**row) for row in result.mappings()]
