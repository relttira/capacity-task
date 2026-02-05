from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class SailingLevelRaw(SQLModel, table=True):    # TODO: Add constraints.
    id: Optional[int] = Field(default=None, primary_key=True)
    origin: str
    destination: str
    origin_port_code: str
    destination_port_code: str
    service_version_and_roundtrip_identifiers: str
    origin_service_version_and_master: str
    destination_service_version_and_master: str
    origin_at_utc: datetime
    offered_capacity_teu: int
