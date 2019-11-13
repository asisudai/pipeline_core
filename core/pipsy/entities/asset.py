'''Asset entity class'''

# imports
from sqlalchemy import (Table, Column, Integer, String, Enum, Index, ForeignKey,
                        UniqueConstraint, Boolean)
from sqlalchemy.orm import relationship
from ..core.pythonx import string_types
from .core import Base
from .project import Project


class Asset(Base):

    __table__ = Table('asset', Base.metadata,

                      Column('id', Integer, primary_key=True),
                      Column('name', String(64), nullable=False),
                      Column('basename', String(64), nullable=False),
                      Column('status', Enum('act', 'dis'), default='act', nullable=False),
                      Column('project_id', Integer, ForeignKey(Project.id), nullable=False),
                      Column('shotgun_id', Integer, nullable=True),
                      Column('kind', Enum('char', 'prop', 'vhcl', 'env', 'fx', 'matte',
                                          'camera', 'light'), nullable=False),
                      # TODO: use library column e.g. AssetLibrary
                      Column('library', Boolean, default=False, nullable=True),
                      Column('description', String(255)),

                      Index('ix_proj_stat_name', 'project_id', 'status', 'name'),
                      Index('ix_proj_stat_kind', 'project_id', 'status', 'kind'),
                      Index('ix_sg', 'shotgun_id'),

                      UniqueConstraint('project_id', 'name', name='uq_proj_name'),
                      UniqueConstraint('project_id', 'basename', name='uq_proj_basename'),
                      UniqueConstraint('shotgun_id', name='uq_sg')
                      )

    _tasks = relationship('Task', backref='asset', lazy='dynamic',
                          order_by='Task.name', cascade="all, delete-orphan")
    _instances = relationship('Instance', backref='asset', lazy='dynamic',
                              order_by='Instance.id', cascade="all, delete-orphan")
    _publishgroups = relationship('PublishGroup', backref='asset', lazy='dynamic',
                                  order_by='PublishGroup.id', cascade="all, delete-orphan")

    @property
    def parent(self):
        '''
        Return Asset parent Project entity.
        '''
        return self.project

    @property
    def tasks(self):
        '''
        Return Asset's list of Tasks.
        '''
        return [t for t in self._tasks if t.status not in t.disabled_statuses()]

    @classmethod
    def find(cls, project=None, name=None, basename=None, kind=None, library=None,
             status=None, id=None, shotgun_id=None):
        '''
        Return Asset instances by query arguments

            Args:
                project     (Project) : parent Project instance.
                name            (str) : Asset name.
                basename        (str) : Asset basename.
                kind        (str/list): Asset kind(s).
                library         (bool): Asset Library.
                status          (str) : Asset status.
                id         (int/list) : Asset id(s).
                shotgun_id (int/list) : Asset shotgun id(s).

            Returns:
                A list of Asset instances matching find arguments.
        '''
        query = cls.query(project=project, name=name, id=id, status=status, shotgun_id=shotgun_id)

        if kind:
            if isinstance(kind, (list, tuple)):
                query = query.filter(cls.kind.in_(kind))
            elif isinstance(kind, string_types):
                query = query.filter(cls.kind == kind)
            else:
                raise ValueError('Invalid argument given {}'.format(kind))

        if basename:
            query = query.filter(cls.basename == basename)

        if library is not None:
            query = query.filter(cls.library == library)

        return query.all()

    @classmethod
    def create(cls, name, project, kind, library=None, status=None, shotgun_id=None):
        '''
        Create a Asset instance.

            Args:
                name            (str) : Asset name.
                project     (Project) : parent Project instance.
                kind             (str): Asset kind.
                status          (str) : Asset status.
                shotgun_id (int/list) : Asset shotgun id(s).

            Returns:
                New Asset Instance.

        '''
        cls.assert_isinstance(project, 'Project')

        data = dict(name=name,
                    basename=name,
                    status=status,
                    project_id=project.id,
                    kind=kind,
                    library=library,
                    shotgun_id=shotgun_id)

        return super(Asset, cls).create(**data)
