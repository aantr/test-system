# import sqlalchemy
# from sqlalchemy import orm
# from .db_session import SqlAlchemyBase
#
#
# class Task(SqlAlchemyBase):
#     __tablename__ = 'task'
#
#     id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
#     problem = orm.relation('Problem', back_populates='task')
