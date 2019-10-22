#!/usr/bin/env python
'''Project entity class'''

# imports
from sqlalchemy import (Table, Column, Integer, String, Enum, Index, UniqueConstraint)
from sqlalchemy.orm import relationship
from .core import Base


class Project(Base):

    __table__ = Table('project', Base.metadata,
                      Column('id', Integer, primary_key=True),
                      Column('name', String(32), nullable=False),
                      Column('status', Enum('act', 'dis', 'hld', 'arc'), default='act',
                             nullable=False),
                      Column('schema', Enum('tv', 'film'), default='film', nullable=False),
                      Column('root', String(128), nullable=False),
                      Column('shotgun_id', Integer),
                      Column('description', String(255)),

                      Index('ix_name', 'name'),
                      Index('ix_sg', 'shotgun_id'),

                      UniqueConstraint('name', name='uq_name'),
                      UniqueConstraint('root', name='uq_root'),
                      UniqueConstraint('shotgun_id', name='uq_sg')
                      )

    _formats = relationship('Format', backref='project', lazy='dynamic',
                            cascade="all, delete-orphan")
    _episodes = relationship('Episode', backref='project', lazy='dynamic',
                             order_by='Episode.name', cascade="all, delete-orphan")
    _sequences = relationship('Sequence', backref='project', lazy='dynamic',
                              order_by='Sequence.name', cascade="all, delete-orphan")
    _shots = relationship('Shot', backref='project', lazy='dynamic',
                          order_by='Shot.name', cascade="all, delete-orphan")
    _assets = relationship('Asset', backref='project', lazy='dynamic',
                           order_by='Asset.name', cascade="all, delete-orphan")
    _tasks = relationship('Task', backref='project', lazy='dynamic',
                          order_by='Task.id', cascade="all, delete-orphan")
    _userprojects = relationship('UserProject', backref='project', lazy='dynamic',
                                 cascade="all, delete-orphan")
    _instances = relationship('Instance', backref='project', lazy='dynamic',
                              order_by='Instance.id', cascade="all, delete-orphan")
    _publishgroups = relationship('PublishGroup', backref='project', lazy='dynamic',
                                  order_by='PublishGroup.id', cascade="all, delete-orphan")
    _publish = relationship('Publish', backref='project', lazy='dynamic',
                            order_by='PublishGroup.id', cascade="all, delete-orphan")

    @classmethod
    def findby_name(cls, name):
        '''Return a Project instance by name'''
        return cls.query().filter(cls.name == name).one()

    @classmethod
    def find(cls, name=None, root=None, format=None, schema=None, status=None,
             id=None, shotgun_id=None):
        '''
        Return Project instances by query arguments

            Args:
                name            (str) : Project name.
                root            (str) : Project root.
                format          (str) : Project format.
                schema          (str) : Project schema.
                status          (str) : Project status.
                id         (int/list) : Project id(s).
                shotgun_id (int/list) : Project shotgun id(s).

            Returns:
                A list of Project instances matching find arguments.

        '''
        query = cls.query(name=name, id=id, status=status, shotgun_id=shotgun_id)

        if format:
            query = query.filter(cls.format == format)

        if schema:
            query = query.filter(cls.schema == schema)

        if root:
            query = query.filter(cls.root == root)

        query = query.order_by(cls.name)
        return query.all()

    @classmethod
    def create(cls, name, root, schema, description='', status=None, shotgun_id=None):
        '''
        Create a new Project instance.

            Args:
                name        (str) : Project name.
                root        (str) : Project linux filesystem root.
                schema      (str) : Project schema e.g. ['tv', 'film']
                description (str) : Project description.
                status      (str) : Project status. default to 'act'.
                shotgun_id  (int) : Project shotgun id.

            Returns:
                New Project instance

        '''
        data = dict(name        = name,
                    shotgun_id  = shotgun_id,
                    schema      = schema,
                    root        = root,
                    status      = status,
                    description = description)

        return super(Project, cls).create(**data)
