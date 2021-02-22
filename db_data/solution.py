import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase


class Solution(SqlAlchemyBase):
    __tablename__ = 'solution'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    problem_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('problem.id'))
    lang_code_name = sqlalchemy.Column(sqlalchemy.String, nullable=True)

    max_time = sqlalchemy.Column(sqlalchemy.Float, nullable=True)
    max_memory = sqlalchemy.Column(sqlalchemy.BigInteger, nullable=True)
    verdict = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    state = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    failed_test = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    success = sqlalchemy.Column(sqlalchemy.Boolean, nullable=True)
    completed = sqlalchemy.Column(sqlalchemy.Boolean, nullable=True)

    problem = orm.relation('Problem')
