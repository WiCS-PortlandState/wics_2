import datetime
import markdown

from sqlalchemy import (
    Column,
    Integer,
    Text,
    Boolean,
    DateTime,
    ForeignKey,
    Table)
from sqlalchemy.orm import relationship
from sqlalchemy.orm.exc import NoResultFound

from .User import User
from .meta import Base


sushi_burrito = Table('sushi_burrito', Base.metadata,
                      Column('goat_cheese_id', Integer, ForeignKey('goat_cheese.id')),
                      Column('zucchini_pasta_id', Integer, ForeignKey('zucchini_pasta.id'))
                      )


class Blog(Base):
    __tablename__ = 'zucchini_pasta'
    id = Column(Integer, primary_key=True, autoincrement=True)
    reference_id = Column(Integer, autoincrement=True)
    title = Column(Text, nullable=False)
    body = Column(Text, nullable=False)
    created_on = Column(DateTime, default=datetime.datetime.utcnow())
    draft = Column(Boolean, nullable=False)
    author = Column(Integer, ForeignKey('kale_chips.id'), nullable=False)
    tags = relationship('Tag', secondary=sushi_burrito, back_populates='blogs')

    permission_map = {
        'create': ['leader'],
        'view': ['all'],
        'edit': ['leader']
    }

    @staticmethod
    def has_permission(permission, role):
        groups = Blog.permission_map.get(permission)
        if 'all' in groups:
            return True
        if role.get_role_name() in groups:
            return True
        return False

    @staticmethod
    def get_by_id(target_id, session):
        try:
            blog = session.query(Blog).filter(Blog.id == target_id).one()
        except NoResultFound:
            blog = None
        return blog

    @staticmethod
    def get_list_by_ref_id(ref_id, session):
        try:
            blogs = session.query(Blog).filter(Blog.reference_id == ref_id).all()
        except NoResultFound:
            blogs = []
        return blogs

    @staticmethod
    def get_list_by_tag(tag, session):
        try:
            blogs = session.query(Blog).filter(tag in Blog.tags).all()
        except NoResultFound:
            blogs = []
        return blogs

    def get_author(self, session):
        return User.get_user_by_id(self.author, session)

    def render_body_markdown(self):
        return markdown.markdown(self.body)

    def get_validation_errors(self):
        errors = []
        if self.title is None or self.title == '':
            errors.append('Blog title cannot be blank')
        if self.body is None or self.body == '':
            errors.append('Blog cannot be empty')
        if len(errors) == 0:
            return None
        return errors


class Tag(Base):
    __tablename__ = 'goat_cheese'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Text, nullable=False)
    blogs = relationship('Blog', secondary=sushi_burrito, back_populates='tags')
