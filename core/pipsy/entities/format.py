#!/usr/bin/env python
'''Format entity class'''

# imports
from sqlalchemy import (Table, Column, Integer, String, Enum, Index, Float,
                        SmallInteger, ForeignKey, UniqueConstraint)
from .core import Base
from .project import Project
from .episode import Episode


class Format(Base):

    __table__ = Table('format', Base.metadata,
                      Column('id', Integer, primary_key=True),
                      Column('name', String(32), nullable=True),
                      Column('status', Enum('act', 'dis'), default='act',
                             nullable=False),
                      Column('resolution_width', SmallInteger, default=1920),
                      Column('resolution_height', SmallInteger, default=1080),
                      Column('resolution_aspect', Float, default=2.4),
                      Column('engine', String(16), nullable=True),
                      Column('fps', Float, default=24.0),
                      Column('project_id', Integer, ForeignKey(Project.id),
                             nullable=False),
                      Column('episode_id', Integer, ForeignKey(Episode.id)),
                    #   Column('sequence_id', Integer, ForeignKey('sequence.id')),
                    #   Column('shot_id', Integer, ForeignKey('shot.id')),
                    #   Column('res_high_width', SmallInteger, default=1920),
                    #   Column('res_high_height', SmallInteger, default=800),
                    #   Column('res_mid_width', SmallInteger, default=1920),
                    #   Column('res_mid_height', SmallInteger, default=800),
                    #   Column('res_low_width', SmallInteger, default=960),
                    #   Column('res_low_height', SmallInteger, default=400),
                    #   Column('handles_in', SmallInteger, default=10),
                    #   Column('handles_out', SmallInteger, default=10),
                    #   Column('rights', String(32), default=''),

                      Index('ix_proj_stat_name', 'project_id', 'name', 'status'),
                      Index('ix_episode', 'episode_id'),
                    #   Index('ix_name_entities', 'name', 'project_id', 'sequence_id', 'shot_id'),
                    #   Index('ix_sequence', 'sequence_id'),

                      UniqueConstraint('project_id', 'name', name='uc_proj_name')
                      )

    def __repr__(self):
        return "{cls}(name='{name}', id={id})".format(cls=self.__class__.__name__,
                                                      name=self.name,
                                                      id=self.id)

    @classmethod
    def find(cls, entity=None, name=None, status=None, id=None):
        '''
        Return Format instances by query arguments

        args:
            entity (Entity) : linked Entity.
            name      (str) : name. defaults to 'default'.
            status    (str) : status.
            id   (int/list) : id.
        '''
        query = cls.query(id=id, status=status)

        if name:
            query = query.filter(cls.name == name)

        if entity:
            if entity.cls_name() == 'Project':
                query = query.filter(cls.project_id == entity.id)
            elif entity.cls_name() == 'Episode':
                query = query.filter(cls.project_id == entity.project.id,
                                     cls.episode_id == entity.id)
            elif entity.cls_name() == 'Sequence':
                query = query.filter(cls.project_id == entity.project.id,
                                     cls.sequence_id == entity.id)
            elif entity.cls_name() == 'Shot':
                query = query.filter(cls.project_id == entity.project.id,
                                     cls.shot_id == entity.id)
            else:
                raise NotImplementedError('entity {!r} not implemented!'.format(entity.cls_name()))

        return query.all()

    @classmethod
    def create(cls, entity, name=None, high_res=None, mid_res=None, low_res=None,
               engine=None, fps=None, aspect=None, handles=None, status='act'):
        '''
        Create a Format.
        Will do an SQL insert call to the db, making this entity permanently available.

        args:
            entity    (Entity) : link the Format to Project, Sequence or Shot.
            name         (str) : name. defaults to 'default'.
            high_res   (tuple) : high resolution (defaults to 1080).
            mid_res    (tuple) : middle resolution (defaults to 1080).
            low_res    (tuple) : low resolution (defaults to 960).
            handles    (tuple) : default in and out handles.
            engine       (str) : render engine.
            fps        (float) : frame per second.
            aspect     (float) : resolution aspect ratio.

        Return new Format
        '''
        (project_id, episode_id, sequence_id, shot_id) = (None, None, None, None)

        if not isinstance(entity, Base):
            raise TypeError('entity arg must be an Entity class.')
        elif entity.cls_name() == 'Project':
            project_id = entity.id
        elif entity.cls_name() == 'Episode':
            project_id = entity.project.id
            episode_id = entity.id
        elif entity.cls_name() == 'Sequence':
            project_id = entity.project.id
            sequence_id = entity.id
        elif entity.cls_name() == 'Shot':
            project_id = entity.project.id
            shot_id = entity.id
        else:
            raise ValueError('entity arg must be a supported Entity cls.')

        data = dict(name            = name,
                    status          = status,
                    project_id      = project_id,
                    episode_id      = episode_id,
                    # sequence_id     = sequence_id,
                    # shot_id         = shot_id,
                    resolution_width  = high_res[0] if high_res else None,
                    resolution_height = high_res[1] if high_res else None,
                    fps               = fps if fps else None,
                    resolution_aspect = aspect if aspect else None,
                    # res_mid_height  = mid_res[1] if mid_res else None,
                    # res_low_width   = low_res[0] if low_res else None,
                    # res_low_height  = low_res[1] if low_res else None,
                    # handles_in      = handles[0] if handles else None,
                    # handles_out     = handles[1] if handles else None,
                    )
        return super(Format, cls).create(**data)
