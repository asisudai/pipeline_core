#!/usr/bin/env python
'''Project entity class'''

# imports
from sqlalchemy import Table, Column, Integer, String, Enum, Index, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.orm.exc import NoResultFound
from .core import Base


class Project(Base):

    __table__ = Table('project', Base.metadata,
                      Column('id', Integer, primary_key=True),
                      Column('shotgun_id', Integer, nullable=True),
                      Column('name', String(32), nullable=False),
                      Column('status', Enum('act', 'dis', 'hld'), default='act', nullable=False),
                      Column('format', Enum('tv', 'film'), default='film', nullable=False),
                      Column('root', String(128), nullable=False),
                      Column('description', String(255)),

                      Index('ix_name', 'name'),
                      Index('ix_sg', 'shotgun_id'),

                      UniqueConstraint('name', name='uq_name'),
                      UniqueConstraint('root', name='uq_root'),
                      UniqueConstraint('shotgun_id', name='uq_sg')
                      )

    def __repr__(self):
        return "{cls}(name='{name}', id={id})".format(cls=self.__class__.__name__,
                                                      name=self.name,
                                                      id=self.id)

    @classmethod
    def findby_name(cls, name):
        '''Return a Project instance by name'''
        return cls._connect().query(cls).filter(cls.name == name).one()

    @classmethod
    def find(cls, name=None, format=None, status=None, root=None,
             id=None, shotgun_id=None):
        '''
        Return Project instances by query arguments

            Args:
                name            (str) : name.
                root            (str) : filesystem root.
                format          (str) : format ['tv', 'film']
                description     (str) : description.
                status          (str) : status. default to 'act'.
                id         (int/list) : id.
                shotgun_id (int/list) : shotgun id.

            Returns:
                A list of Project instances

        '''
        query = cls._connect().query(cls)

        if name:
            query = query.filter(cls.name == name)

        if format:
            query = query.filter(cls.format == format)

        if root:
            query = query.filter(cls.root == root)

        if status is None:
            pass
        elif isinstance(status, (list, tuple)):
            query = query.filter(cls.status.in_(status))
        elif status:
            query = query.filter(cls.status == status)

        if shotgun_id:
            if isinstance(shotgun_id, (int, long)):
                query = query.filter(cls.shotgun_id == shotgun_id)
            elif isinstance(shotgun_id, (list, tuple)):
                query = query.filter(cls.shotgun_id.in_(shotgun_id))
            else:
                raise ValueError('Invalid argument given {}'.format(type(shotgun_id)))

        if id:
            if isinstance(id, (int, long)):
                query = query.filter(cls.id == id)
            elif isinstance(id, (list, tuple)):
                query = query.filter(cls.id.in_(id))
            else:
                raise ValueError('Invalid argument given {}'.format(type(id)))

        query = query.order_by(cls.name)
        return query.all()

    @classmethod
    def create(cls, name, root, format='tv', description='', status=None, shotgun_id=None):
        '''
        Create a new project.

            Args:
                name        (str) : name.
                root        (str) : filesystem root.
                format      (str) : format ['tv', 'film']
                description (str) : description.
                status      (str) : status. default to 'act'.
                shotgun_id  (int) : shotgun id.
            
            Returns:
                New Project instance

        '''
        data = dict(name        = name,
                    shotgun_id  = shotgun_id,
                    format      = format,
                    root        = root,
                    status      = status,
                    description = description)

        return super(Project, cls).create(**data)
