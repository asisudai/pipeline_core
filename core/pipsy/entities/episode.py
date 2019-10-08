'''Episode entity class'''

# imports
from sqlalchemy import (Table, Column, Integer, String, Enum, Index,
                        ForeignKey, UniqueConstraint)
# from sqlalchemy.orm import relationship
from .core import Base
from .project import Project


class Episode(Base):

    __table__ = Table('episode', Base.metadata,
                      Column('id', Integer, primary_key=True),
                      Column('name', String(32), nullable=False),
                      Column('basename', String(32), nullable=False),
                      Column('status', Enum('act', 'dis'), default='act', nullable=False),
                      Column('project_id', Integer, ForeignKey(Project.id), nullable=False),
                      Column('shotgun_id', Integer),

                      Index('ix_proj_name', 'project_id', 'name', 'status'),
                      Index('ix_sg', 'shotgun_id'),

                      UniqueConstraint('project_id', 'name', name='uq_proj_name'),
                      UniqueConstraint('project_id', 'basename', name='uq_proj_basename'),
                      UniqueConstraint('shotgun_id', name='uq_sg')
                      )

    @classmethod
    def find(cls, project=None, name=None, status=None, id=None, shotgun_id=None):
        '''
        Return Episode instances by query arguments

            Args:
                project     (Project) : parent Project instance.
                name            (str) : Episode name.
                status          (str) : Episode status.
                id         (int/list) : Episode id(s).
                shotgun_id (int/list) : Epsiode shotgun id(s).

            Returns:
                A list of Episode instances matching find arguments.
        '''
        query = cls.query(id=id, status=status, shotgun_id=shotgun_id)

        if project:
            query = query.filter(cls.project_id == project.id)

        if name:
            query = query.filter(cls.name == name)

        return query.all()

    @classmethod
    def create(cls, name, project, status=None, shotgun_id=None):
        '''
        Create an Episode instance.

            Args:
                name            (str) : Episode name.
                project     (Project) : parent Project instance.
                status          (str) : Episode status.
                shotgun_id (int/list) : Epsiode shotgun id(s).

            Returns:
                New Episode instance.
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
                    shotgun_id=shotgun_id)

        return super(Episode, cls).create(**data)