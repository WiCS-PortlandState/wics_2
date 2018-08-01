import datetime
import hashlib
import random
import uuid

from sqlalchemy import (
    Column,
    Index,
    Integer,
    Text,
    ForeignKey,
    Boolean,
    DateTime,
    or_, and_)
from sqlalchemy.orm import relationship
from sqlalchemy.orm.exc import NoResultFound

from .meta import Base


class User(Base):
    __tablename__ = 'kale_chips'
    id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(Text)
    last_name = Column(Text)
    nickname = Column(Text, nullable=False)
    username = Column(Text, unique=True, nullable=False)
    password = Column(Text, nullable=False)
    email = Column(Text)
    salt_id = Column(Integer, ForeignKey('fried_lettuce.id'))
    salt = relationship('Salt')
    role_id = Column(Integer, ForeignKey('organic_granola.id'))
    role = relationship('Role')
    active = Column(Boolean, default=True)

    permission_map = {
        'view': ['admin', 'leader', 'self'],
        'edit': ['self', 'admin', 'leader'],
        'create': ['self', 'admin'],
        'delete': ['self', 'admin', 'leader'],
    }

    @staticmethod
    def get_user_by_id(target_id, db_session):
        try:
            user = db_session.query(User).filter(User.id == target_id).one()
        except NoResultFound:
            user = None
        return user

    @staticmethod
    def get_user_by_username(username, db_session):
        try:
            user = db_session.query(User).filter(User.username == username).one()
        except NoResultFound:
            user = None
        return user

    @staticmethod
    def get_by_username_or_email(username, email, db_session):
        try:
            users = db_session\
                .query(User)\
                .filter(and_(or_(User.username == username, User.email == email), User.active))\
                .all()
        except NoResultFound:
            users = []
        return users

    @staticmethod
    def authenticate(username, password, db_session):
        user = User.get_user_by_username(username, db_session)
        if user is not None:
            salted = (password + user.salt.value).encode('utf8')
            hashed_pw = hashlib.sha512(salted).hexdigest()
            if user.password == hashed_pw:
                return user
        return None

    def __init__(self, username, password, first_name, last_name, nickname, email):
        self.username = username
        self.password = password
        self.first_name = first_name
        self.last_name = last_name
        self.nickname = nickname
        self.email = email

    def has_permissions_on_others(self, permission):
        if self.role.get_role_name() in User.permission_map[permission]:
            return True
        return False

    def promote_other(self, other_user, db_session):
        if self.role.compare(other_user.role) <= 0:
            return False
        other_user.role = other_user.role.get_promotion(db_session)

    def salt_password(self, db_session):
        salts = Salt.get_all(db_session)
        salt = random.choice(salts)
        salted = (self.password + salt.value).encode('utf8')
        self.password = hashlib.sha512(salted).hexdigest()
        self.salt = salt

    def before_save(self, db_session):
        self.salt_password(db_session)
        self.role = Role.get_default(db_session)

    def get_validation_errors(self, db_session):
        errors = []
        if self.username is None or self.username == '':
            errors.append('Username cannot be blank')
        if self.first_name is None or self.first_name == '':
            errors.append('First name cannot be blank')
        if self.last_name is None or self.last_name == '':
            errors.append('Last name cannot be blank')
        if self.email is None or self.email == '':
            errors.append('Email cannot be blank')
        if User.get_user_by_username(self.username, db_session) is not None:
            errors.append('That username is already taken')
        if len(errors) != 0:
            return '\r\n'.join(errors)
        return None

    def to_dict(self):
        return dict({
            'first_name': self.first_name,
            'last_name': self.last_name,
            'nickname': self.nickname,
            'role': self.role.name,
            'email': self.email,
            'username': self.username,
        })


Index('username_index', User.username, unique=True)


class Salt(Base):
    __tablename__ = 'fried_lettuce'
    id = Column(Integer, primary_key=True, autoincrement=True)
    value = Column(Text, nullable=False)

    @staticmethod
    def get_all(db_session):
        try:
            salts = db_session.query(Salt).all()
        except NoResultFound:
            salts = []
        return salts


class Role(Base):
    __tablename__ = 'organic_granola'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Text, nullable=False)
    admin = Column(Boolean, nullable=False, default=False)
    designer = Column(Boolean, nullable=False, default=False)
    leader = Column(Boolean, nullable=False, default=False)
    member = Column(Boolean, nullable=False, default=True)

    permission_tree = {
        'admin': 99,
        'leader': 98,
        'designer': 50,
        'member': 0,
    }

    @staticmethod
    def get_default(db_session):
        return db_session.query(Role).filter(Role.member).one()

    @staticmethod
    def get_by_id(target_id, db_session):
        try:
            role = db_session.query(Role).filter(Role.id == target_id).one()
        except NoResultFound:
            role = None
        return role

    def compare(self, other):
        my_role = self.get_role_name()
        other_role = other.get_role_name()
        return Role.permission_tree[my_role] - Role.permission_tree[other_role]

    def get_promotion(self, db_session):
        role_name = self.get_role_name()
        query_name = None
        if role_name == 'member':
            query_name = 'singer-songwriter'
        elif role_name == 'designer':
            query_name = 'poet'
        elif role_name == 'leader':
            query_name = 'beyonce'
        if query_name is None:
            raise NoResultFound
        return db_session.query(Role).filter(Role.name == query_name).one()

    def get_role_name(self):
        if self.admin:
            return 'admin'
        if self.leader:
            return 'leader'
        if self.designer:
            return 'designer'
        return 'member'


class UserInvitation(Base):
    __tablename__ = 'avocado_toast'
    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(Text, nullable=False)
    invite_date = Column(DateTime, nullable=False, default=datetime.datetime.utcnow())
    expire_date = Column(DateTime, nullable=False)
    link_hash = Column(Text, nullable=False, default=uuid.uuid4().hex)

    permission_map = {
        'create': ['admin', 'leader'],
        'view': ['admin', 'leader'],
        'delete': ['admin', 'leader'],
    }

    @staticmethod
    def validate(invite_hash, db_session):
        try:
            invite = db_session.query(UserInvitation).filter(UserInvitation.link_hash == invite_hash).one()
        except NoResultFound:
            invite = None
        if invite is not None and datetime.datetime.utcnow() <= invite.expire_date:
            return invite
        return None

    @staticmethod
    def validate_permissions(action, user):
        if user.role.get_role_name() in UserInvitation.permission_map[action]:
            return True
        return False
    
    @staticmethod
    def create_invite(email, days_valid, db_session):
        invite = UserInvitation()
        invite.email = email
        invite.invite_date = datetime.datetime.utcnow()
        if days_valid is None or days_valid < 1:
            days_valid = 5
        invite.expire_date = datetime.datetime.utcnow() + datetime.timedelta(days=days_valid)
        invite.link_hash = uuid.uuid4().hex
        db_session.add(invite)
        return invite
