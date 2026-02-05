from datetime import date

from pydantic import BaseModel


class WeeklyCapacity(BaseModel):
    week_start_date: date
    week_no: int
    offered_capacity_teu: int
