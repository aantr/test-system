import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase


class GroupMember(SqlAlchemyBase):
    __tablename__ = 'group_member'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    member_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('user.id'))
    member = sqlalchemy.orm.relation('User')
    group_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('group.id'))
    group = sqlalchemy.orm.relation('Group')


class Group(SqlAlchemyBase):
    __tablename__ = 'group'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)

    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('user.id'))
    user = orm.relation('User')
    join_action_str_id = sqlalchemy.Column(sqlalchemy.String,
                                           sqlalchemy.ForeignKey('action.str_id'),
                                           nullable=True)
    join_action = orm.relation('Action')

