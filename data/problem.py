import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase


class Problem(SqlAlchemyBase):
    __tablename__ = 'problem'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String)

    time_limit = sqlalchemy.Column(sqlalchemy.Float, nullable=True)
    memory_limit = sqlalchemy.Column(sqlalchemy.BigInteger, nullable=True)

    solution = orm.relation('Solution', back_populates='problem')
