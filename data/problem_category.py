import sqlalchemy
from .db_session import SqlAlchemyBase


class ProblemCategory(SqlAlchemyBase):
    __tablename__ = 'problem_category'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True,
                           autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
