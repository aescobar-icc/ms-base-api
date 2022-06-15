from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, create_engine
from sqlalchemy.orm import declarative_base

from lib.db.sql.connection import SqlConnection

db = SqlConnection.connect(None)
Base = db.Model #declarative_base()
class Articles(Base):
    __tablename__ = 'articles'
    id = Column(Integer, primary_key=True)
    #user_id = Column(Integer, ForeignKey('users.id'))
    user_id = Column(Integer)
    title = Column(String)

    @staticmethod
    def get_all():
        return Articles.query.all()


class PosthgresTest:
    @staticmethod
    def articles_all_test():
        print("[PosthgresTest] 1.- testing get all articles")
        
        print(Articles.get_all())

