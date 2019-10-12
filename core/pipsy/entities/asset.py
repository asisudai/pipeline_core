'''Asset entity class'''

# imports
from sqlalchemy import (Table, Column, Integer, String, Enum, Index, ForeignKey, UniqueConstraint)
# from sqlalchemy.orm import relationship
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
                      Column('type', Enum('char', 'prop', 'vhcl', 'env', 'fx', 'matte',
                                          'camera', 'light'), nullable=False),
                      #   Column('library_type', Enum('camera', 'light', 'backdrop',
                      #                               'shaderef', 'fugazi', 'rigguide'), nullable=True),
                      Column('description', String(255)),

                      Index('ix_proj_stat_name', 'project_id', 'status', 'name'),
                      Index('ix_proj_stat_typ', 'project_id', 'status', 'type'),
                      Index('ix_sg', 'shotgun_id'),

                      UniqueConstraint('project_id', 'name', name='uq_proj_name'),
                      UniqueConstraint('shotgun_id', name='uq_sg')
                      )

    @property
    def parent(self):
        '''
        Return Asset parent Project entity.
        '''
        return self.project

    @classmethod
    def find(cls, project=None, name=None, basename=None, type=None, status=None,
             id=None, shotgun_id=None):
        '''
        Return Asset instances by query arguments

            Args:
                project     (Project) : parent Project instance.
                name            (str) : Asset name.
                basename        (str) : Asset basename.
                type        (str/list): Asset type(s).
                status          (str) : Asset status.
                id         (int/list) : Asset id(s).
                shotgun_id (int/list) : Asset shotgun id(s).

            Returns:
                A list of Asset instances matching find arguments.
        '''
        query = cls.query(project=project, name=name, id=id, status=status, shotgun_id=shotgun_id)

        if type:
            if isinstance(type, (list, tuple)):
                query = query.filter(cls.type.in_(type))
            elif isinstance(type, basestring):
                query = query.filter(cls.type == type)
            else:
                raise ValueError('Invalid argument given {}'.format(type))

        if basename:
            query = query.filter(cls.basename == basename)

        return query.all()

    @classmethod
    def create(cls, name, project, type, status=None, shotgun_id=None):
        '''
        Create a Asset instance.

            Args:
                name            (str) : Asset name.
                project     (Project) : parent Project instance.
                type             (str): Asset type.
                status          (str) : Asset status.
                shotgun_id (int/list) : Asset shotgun id(s).

            Returns:
                New Asset Instance.

        '''
        if not isinstance(project, Base):
            raise TypeError('project arg must be an Entity class. Given {!r}'
                            .format(type(project)))
        elif project.cls_name() != 'Project':
            raise TypeError('project arg must be an Project class. Given {!r}'
                            .format(type(project)))

        data = dict(name=name,
                    basename=name,
                    status=status,
                    project_id=project.id,
                    type=type,
                    shotgun_id=shotgun_id)

        return super(Asset, cls).create(**data)
