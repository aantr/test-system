import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase


class Image(SqlAlchemyBase):
    __tablename__ = 'image'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    extension = sqlalchemy.Column(sqlalchemy.String)

    @staticmethod
    def get_extensions():
        return {'png', 'jpg', 'jpeg', 'gif', 'bmp'}

    def get_name(self):
        return f'{self.id}.{self.extension}'
