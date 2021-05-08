import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase


class ProblemTests(SqlAlchemyBase):
    __tablename__ = 'problem_tests'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)

    @staticmethod
    def get_extensions():
        return {'zip'}
