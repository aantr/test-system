import sqlalchemy
from .db_session import SqlAlchemyBase


class Action(SqlAlchemyBase):
    __tablename__ = 'action'

    str_id = sqlalchemy.Column(sqlalchemy.String, primary_key=True)
    url = sqlalchemy.Column(sqlalchemy.String)
    description = sqlalchemy.Column(sqlalchemy.String)
