from csv import DictReader
from datetime import datetime
from pathlib import Path
from typing import Annotated

from fastapi import Depends
from sqlmodel import Session, create_engine, SQLModel

from app.database.models.SailingLevelRaw import SailingLevelRaw


class SQLiteHandler:
    DATABASE_DIR = Path(__file__).parent.resolve()
    INIT_DATA_PATH = DATABASE_DIR / 'init_data' / 'sailing_level_raw.csv'

    SQLITE_FILE_NAME = 'database.db'
    SQLITE_URL = f'sqlite:///{DATABASE_DIR / SQLITE_FILE_NAME}'     # TODO: Move constants to a config?
    CONNECT_ARGS = {'check_same_thread': False}

    ENGINE = create_engine(SQLITE_URL, connect_args=CONNECT_ARGS)
    
    @staticmethod
    def init_database() -> None:
        SQLModel.metadata.drop_all(SQLiteHandler.ENGINE)
        SQLModel.metadata.create_all(SQLiteHandler.ENGINE)
        SQLiteHandler.import_csv_data(str(SQLiteHandler.INIT_DATA_PATH))

    @staticmethod
    def get_session():  # TODO: Add return type?
        with Session(SQLiteHandler.ENGINE) as session:
            yield session
    
    SessionDep = Annotated[Session, Depends(get_session)]   # TODO: Move?
    
    @staticmethod
    def import_csv_data(csv_file_path: str):
        with Session(SQLiteHandler.ENGINE) as session:
            with open(csv_file_path, mode='r', encoding='utf-8') as f:
                reader = DictReader(f)
                sailings = []

                for row in reader:
                    sailing = SailingLevelRaw(
                        origin=row['ORIGIN'],
                        destination=row['DESTINATION'],
                        origin_port_code=row['ORIGIN_PORT_CODE'],
                        destination_port_code=row['DESTINATION_PORT_CODE'],
                        # NOTE: Typo in following CSV header is propagated.
                        service_version_and_roundtrip_identfiers=row['SERVICE_VERSION_AND_ROUNDTRIP_IDENTFIERS'],  
                        origin_service_version_and_master=row['ORIGIN_SERVICE_VERSION_AND_MASTER'],
                        destination_service_version_and_master=row['DESTINATION_SERVICE_VERSION_AND_MASTER'],
                        origin_at_utc=datetime.fromisoformat(row['ORIGIN_AT_UTC']),
                        offered_capacity_teu=int(row['OFFERED_CAPACITY_TEU'])
                    )
                    sailings.append(sailing)
                
            session.add_all(sailings)
            session.commit()
