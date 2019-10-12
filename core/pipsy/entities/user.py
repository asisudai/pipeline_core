'''User entity class'''

# imports
from sqlalchemy import (Table, Column, Integer, String, Enum, Index, UniqueConstraint)
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from .core import Base


class User(Base):

    __table__ = Table('user', Base.metadata,

                      Column('id', Integer, primary_key=True),
                      Column('status', Enum('act', 'dis'), default='act', nullable=False),
                      Column('first_name', String(32), nullable=False),
                      Column('last_name', String(32), nullable=False),
                      Column('login', String(32), nullable=False),
                      Column('email', String(50), nullable=False),
                      Column('shotgun_id', Integer, nullable=True),

                      Index('ix_login', 'login'),
                      Index('ix_email', 'email'),
                      Index('ix_status', 'status'),
                      Index('ix_sg', 'shotgun_id'),

                      UniqueConstraint('login', name='uq_login'),
                      UniqueConstraint('email', name='uq_email'),
                      UniqueConstraint('shotgun_id', name='uq_sg')
                      )

    _usertasks = relationship('UserTask', backref='user', lazy='dynamic',
                              cascade="all, delete-orphan")

    def __repr__(self):
        return "{cls}(login='{login}', id={id})".format(cls=self.__class__.__name__,
                                                        login=self.login,
                                                        id=self.id)

    @hybrid_property
    def fullname(self):
        '''
        Return User fullname string as "{first_name} {last_name}".
        '''
        return '{} {}'.format(self.first_name, self.last_name)

    @fullname.expression
    def fullname(cls):
        return (cls.first_name + " " + cls.last_name)

    @property
    def tasks(self):
        from . task import Task
        return Task.find(user=self)

    @classmethod
    def find(cls, first_name=None, last_name=None, fullname=None, login=None,
             email=None, status=None, id=None, shotgun_id=None):
        '''
        Return User instances by query arguments

            Args:
                first_name      (str) : User first name.
                last_name       (str) : User last name.
                fullname        (str) : User fullname (hybrid).
                login           (str) : User login.
                email           (str) : User email.
                status        (Status): User status.
                id         (int/list) : User id(s)
                shotgun_id (int/list) : User shotgun id(s)

            Returns:
                A list of User instances matching find arguments.
        '''
        query = cls.query(id=id, status=status, shotgun_id=shotgun_id)

        if first_name:
            query = query.filter(cls.first_name == first_name)

        if last_name:
            query = query.filter(cls.last_name == last_name)

        if fullname:
            query = query.filter(cls.fullname == fullname)

        if login:
            query = query.filter(cls.login == login)

        if email:
            query = query.filter(cls.email == email)

        return query.all()

    @classmethod
    def create(cls, first_name, last_name, login, email, status=None, shotgun_id=None):
        '''
        Create a User instance.

            Args:
                first_name      (str) : User first name.
                last_name       (str) : User last name.
                login           (str) : User login.
                email           (str) : User email.
                status        (Status): User status.
                shotgun_id (int/list) : User shotgun id(s)

            Returns:
                New User Instance.

        '''
        data = dict(first_name=first_name,
                    last_name=last_name,
                    login=login,
                    email=email,
                    status=status,
                    shotgun_id=shotgun_id)

        return super(User, cls).create(**data)
