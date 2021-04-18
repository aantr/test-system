import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase


class TestResult(SqlAlchemyBase):
    __tablename__ = 'test_result'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
