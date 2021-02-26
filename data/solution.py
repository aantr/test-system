import datetime
import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase
import sqlalchemy.sql.sqltypes as sqltypes


class Solution(SqlAlchemyBase):
    __tablename__ = 'solution'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    problem_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('problem.id'))
    problem = orm.relation('Problem')
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('user.id'))
    user = orm.relation('User')
    lang_code_name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    sent_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)

    state = sqlalchemy.Column(sqltypes.Integer, nullable=True)
    state_arg = sqlalchemy.Column(sqltypes.Integer, nullable=True)

    max_time = sqlalchemy.Column(sqlalchemy.Float, nullable=True)
    max_memory = sqlalchemy.Column(sqlalchemy.BigInteger, nullable=True)
    failed_test = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    success = sqlalchemy.Column(sqlalchemy.Boolean, nullable=True)
    completed = sqlalchemy.Column(sqlalchemy.Boolean, nullable=True)
