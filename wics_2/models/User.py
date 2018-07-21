from sqlalchemy import (
    Column,
    Index,
    Integer,
    Text,
    ForeignKey, Boolean)
from .meta import Base


class User(Base):
    __tablename__ = 'kale_chips'
    id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(Text)
    last_name = Column(Text)
    nickname = Column(Text, nullable=False)
    username = Column(Text, unique=True, nullable=False)
    password = Column(Text, nullable=False)
    salt = Column(Integer, ForeignKey('fried_lettuce.id'), nullable=False)
    role = Column(Integer, ForeignKey('organic_granola.id'), nullable=False)


Index('username_index', User.username, unique=True)


class Salt(Base):
    __tablename__ = 'fried_lettuce'
    id = Column(Integer, primary_key=True, autoincrement=True)
    value = Column(Text, nullable=False)


class Role(Base):
    __tablename__ = 'organic_granola'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Text, nullable=False)
    admin = Column(Boolean, nullable=False, default=False)
    designer = Column(Boolean, nullable=False, default=False)
    leader = Column(Boolean, nullable=False, default=False)
    member = Column(Boolean, nullable=False, default=True)
