import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase


class Invite(SqlAlchemyBase):
    __tablename__ = 'invite'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)

    user_to_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('user.id'))
    user_to = orm.relation('User', foreign_keys=[user_to_id])

    user_from_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('user.id'))
    user_from = orm.relation('User', foreign_keys=[user_from_id])

    action = sqlalchemy.Column(sqlalchemy.String)
    description = sqlalchemy.Column(sqlalchemy.String)
