import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase


class SourceCode(SqlAlchemyBase):
    __tablename__ = 'source_code'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
