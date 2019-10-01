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
                      Column('name', String(32), nullable=True),
                      Column('basename', String(32), nullable=True),
                      Column('status', Enum('act', 'dis'),
                             default='act', nullable=False),
                      Column('project_id', Integer, ForeignKey(Project.id),
                             nullable=False),
                      Column('shotgun_id', Integer, nullable=True),
                      Index('ix_proj_name', 'project_id', 'name', 'status'),
                      Index('ix_sg', 'shotgun_id'),

                      UniqueConstraint('project_id', 'name',
                                       name='uc_proj_name'),
                      UniqueConstraint('shotgun_id', name='uc_sg')
                      )

    def __repr__(self):
        return "{cls}(name='{name}', id={id})".format(cls=self.__class__.__name__,
                                                      name=self.name,
                                                      id=self.id)

    @classmethod
    def find(cls, project=None, name=None, status=None,
             id=None, shotgun_id=None):
        '''
        Return Episode instances by query arguments

            Args:
                project     (Project) : project.
                name            (str) : name.
                status          (str) : status.
                id         (int/list) : id.
                shotgun_id (int/list) : shotgun id.
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
        Create a project.
        Will do an SQL insert call to the db, making this entity permanently available.

            name        (str) : name.
            root        (str) : filesystem root.
            format      (str) : format ['tv', 'film']
            status      (str) : status. default to 'act'.
            shotgun_id  (int) : shotgun id.

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
