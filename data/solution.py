import datetime
import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase
import sqlalchemy.sql.sqltypes as sqltypes


class Solution(SqlAlchemyBase):
    __tablename__ = 'solution'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    lang_code_name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    sent_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)

    problem_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('problem.id'))
    problem = orm.relation('Problem')

    test_result_id = sqlalchemy.Column(sqlalchemy.Integer,
                                       sqlalchemy.ForeignKey('test_result.id'))
    test_result = orm.relation('TestResult')

    source_code_id = sqlalchemy.Column(sqlalchemy.Integer,
                                       sqlalchemy.ForeignKey('source_code.id'))
    source_code = orm.relation('SourceCode')

    session_id = sqlalchemy.Column(sqlalchemy.Integer,
                                   sqlalchemy.ForeignKey('session.id'), nullable=True)
    session = orm.relation('Session')

    state = sqlalchemy.Column(sqltypes.Integer, nullable=True)
    state_arg = sqlalchemy.Column(sqltypes.Integer, nullable=True)

    max_time = sqlalchemy.Column(sqlalchemy.Float, nullable=True)
    max_memory = sqlalchemy.Column(sqlalchemy.BigInteger, nullable=True)
    failed_test = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    success = sqlalchemy.Column(sqlalchemy.Boolean, nullable=True)
    completed = sqlalchemy.Column(sqlalchemy.Boolean, nullable=True)

    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('user.id'))
    user = orm.relation('User')
