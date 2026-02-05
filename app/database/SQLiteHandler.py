from csv import DictReader
from datetime import datetime
from pathlib import Path
from typing import Generator

from sqlmodel import Session, create_engine, SQLModel

from app.database.models.SailingLevelRaw import SailingLevelRaw


class SQLiteHandler:
    DATABASE_DIR = Path(__file__).parent.resolve()
    INIT_DATA_PATH = DATABASE_DIR / 'init_data' / 'sailing_level_raw.csv'

    SQLITE_FILE_NAME = 'database.db'    # TODO: Move constants to a config?
    SQLITE_URL = f'sqlite:///{DATABASE_DIR / SQLITE_FILE_NAME}'
    CONNECT_ARGS = {'check_same_thread': False}

    def __init__(self):
        self.engine = create_engine(SQLiteHandler.SQLITE_URL, connect_args=SQLiteHandler.CONNECT_ARGS)
    
    def load_data(self) -> None:
        SQLModel.metadata.drop_all(self.engine)
        SQLModel.metadata.create_all(self.engine)
        self.import_csv_data(str(self.INIT_DATA_PATH))

    def get_session(self) -> Generator[Session, None, None]:
        with Session(self.engine) as session:
            yield session
    
    def import_csv_data(self, csv_file_path: str):
        with Session(self.engine) as session:
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
