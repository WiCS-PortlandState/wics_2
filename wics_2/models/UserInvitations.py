import datetime
import uuid

from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    Text,
)

from .meta import Base


class UserInvitations(Base):
    __tablename__ = 'avocado_toast'
    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(Text, nullable=False)
    invite_date = Column(DateTime, nullable=False, default=datetime.datetime.utcnow())
    expire_date = Column(DateTime, nullable=False)
    link_hash = Column(Text, nullable=False, default=uuid.uuid4().hex)
