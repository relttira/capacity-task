from datetime import date
from typing import Annotated

from fastapi import Depends, FastAPI
from sqlalchemy.engine.cursor import CursorResult
from sqlmodel import Session

from app.api.models.WeeklyCapacity import WeeklyCapacity
from app.database.SQLiteHandler import SQLiteHandler
from app.database.queries.capacity import CAPACITY


app = FastAPI()

database = SQLiteHandler()
SessionDep = Annotated[Session, Depends(database.get_session)]

@app.on_event('startup')    # TODO: Use lifespan event handlers.
def on_startup():
    database.load_data()

@app.get('/capacity')
def get_capacity(session: SessionDep, date_from: date, date_to: date) -> list[WeeklyCapacity]:   # TODO: Add constraints?
    params = {'date_from': date_from, 'date_to': date_to}
    result: CursorResult = session.exec(statement=CAPACITY, params=params)
    return [WeeklyCapacity(**row) for row in result.mappings()]
