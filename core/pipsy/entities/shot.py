'''Shot entity class'''

# imports
from sqlalchemy import (Table, Column, Integer, String, Enum, Index, SmallInteger,
                        ForeignKey, UniqueConstraint)
# from sqlalchemy.orm import relationship
from .core import Base
from .project import Project
from .sequence import Sequence


class Shot(Base):

    __table__ = Table('shot', Base.metadata,
                      Column('id', Integer, primary_key=True),
                      Column('name', String(32), nullable=False),
                      Column('basename', String(32), nullable=False),
                      Column('status', Enum('act', 'dis'), default='act', nullable=False),
                      Column('project_id', Integer, ForeignKey(Project.id), nullable=False),
                      Column('sequence_id', Integer, ForeignKey(Sequence.id)),
                      Column('shotgun_id', Integer),
                      Column('cut_in', Integer),
                      Column('cut_out', Integer),
                      Column('cut_order', SmallInteger),
                      Column('handles_in', SmallInteger),
                      Column('handles_out', SmallInteger),
                      Column('description', String(255)),

                      Index('ix_proj_seq_name', 'status', 'project_id', 'sequence_id', 'name'),
                      Index('ix_seq_name', 'sequence_id', 'name'),
                      Index('ix_sg', 'shotgun_id'),

                      UniqueConstraint('sequence_id', 'name', name='uq_seq_name'),
                      UniqueConstraint('shotgun_id', name='uq_sg')
                      )

    @property
    def parent(self):
        '''
        Return Shot parent Sequence entity.
        '''
        return self.sequence

    @classmethod
    def find(cls, project=None, sequence=None, name=None, basename=None, status=None,
             id=None, shotgun_id=None):
        '''
        Return Shot instances by query arguments

            Args:
                project     (Project) : parent Project instance.
                sequence   (Sequence) : parent Sequence instance (optional).
                name            (str) : Shot name.
                basename        (str) : Shot basename.
                status          (str) : Shot status.
                id         (int/list) : Shot id(s).
                shotgun_id (int/list) : Shot shotgun id(s).

            Returns:
                A list of Shot instances matching find arguments.
        '''
        query = cls.query(project=project, name=name, id=id, status=status, shotgun_id=shotgun_id)

        if sequence:
            query = query.filter(cls.sequence_id == sequence.id)

        if basename:
            query = query.filter(cls.basename == basename)

        return query.all()

    @classmethod
    def create(cls, name, project, sequence, status=None, shotgun_id=None):
        '''
        Create a Shot instance.

            Args:
                name            (str) : Shot name.
                project     (Project) : parent Project instance.
                sequence   (Sequence) : parent Sequence instance.
                status          (str) : Shot status.
                shotgun_id (int/list) : Shot shotgun id(s).

            Returns:
                New Shot Instance.

        '''
        if not isinstance(project, Base):
            raise TypeError('project arg must be an Entity class. Given {!r}'
                            .format(type(project)))
        elif project.cls_name() != 'Project':
            raise TypeError('project arg must be an Project class. Given {!r}'
                            .format(type(project)))

        if not isinstance(sequence, Base):
            raise TypeError('episode arg must be an Entity class. Given {!r}'
                            .format(type(sequence)))
        elif sequence.cls_name() != 'Sequence':
            raise TypeError('episode arg must be an Sequence class. Given {!r}'
                            .format(type(sequence)))

        data = dict(name=name,
                    basename=name,
                    status=status,
                    project_id=project.id,
                    sequence_id=sequence.id,
                    shotgun_id=shotgun_id)

        return super(Shot, cls).create(**data)
