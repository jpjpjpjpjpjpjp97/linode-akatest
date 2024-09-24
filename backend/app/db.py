from decouple import config
from sqlmodel import SQLModel, create_engine

# from item.models import Item
# from group.models import Group

# Database setup
sqlite_file_name = config('SQL_FILE_NAME')
sqlite_url = f'sqlite:///{sqlite_file_name}'
connect_args = {'check_same_thread': False}
engine = create_engine(sqlite_url, echo=False, connect_args=connect_args)
# engine = create_engine(sqlite_url, echo=True, connect_args=connect_args)


def drop_tables():
    SQLModel.metadata.drop_all(engine)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
