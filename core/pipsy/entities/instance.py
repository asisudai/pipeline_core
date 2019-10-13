'''Instance entity class'''

# imports
from sqlalchemy import (Table, Column, Integer, String, Enum, Index, DateTime,
                        ForeignKey, UniqueConstraint)
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.sql import func
# from sqlalchemy.orm import relationship
from .core import Base
from .project import Project
from .sequence import Sequence
from .shot import Shot
from .asset import Asset


class Instance(Base):

    __table__ = Table('instance', Base.metadata,

                      Column('id', Integer, primary_key=True),
                      Column('name', String(64), nullable=False),
                      Column('status', Enum('dis', 'act'), default='act', nullable=False),
                      Column('project_id', Integer, ForeignKey(Project.id), nullable=False),
                      Column('sequence_id', Integer, ForeignKey(Sequence.id)),
                      Column('shot_id', Integer, ForeignKey(Shot.id)),
                      Column('asset_id', Integer, ForeignKey(Asset.id), nullable=False),
                      Column('shotgun_id', Integer),
                      Column('description', String(255)),
                      # TODO: MySQL server time seems to be different then host. Sync server time.
                      # SELECT NOW();
                      Column('created', DateTime(timezone=True), server_default=func.now()),
                      Column('updated', DateTime(timezone=True), onupdate=func.now()),

                      Index('ix_proj_seq_name', 'project_id', 'sequence_id', 'name'),
                      Index('ix_proj_shot_name', 'project_id', 'shot_id', 'name'),
                      Index('ix_shot_asset', 'asset_id', 'shot_id'),
                      Index('ix_sg', 'shotgun_id'),

                      UniqueConstraint('sequence_id', 'name', name='uq_seq_name'),
                      UniqueConstraint('shot_id', 'name', name='uq_shot_name'),
                      UniqueConstraint('shotgun_id', name='uq_sg')

                      )

    @property
    def parent(self):
        '''
        Return Instance parent.
        Parent could be Sequence, Shot or Asset entity.
        '''
        if self.shot_id:
            return self.shot
        elif self.sequence_id:
            return self.sequence
        elif self.asset_id:
            return self.asset

    @hybrid_property
    def fullname(self):
        '''
        Return Instance fullname string.
        {episode.name}_{sequence.name}_{shot.name}_{instance.name} or
        {sequence.name}_{shot.name}_{instance.name}
        '''
        return '{}_{}'.format(self.shot.fullname, self.name)

    @classmethod
    def find(cls, project=None, entity=None, name=None, asset=None, status=None,
             id=None, shotgun_id=None):
        '''
        Return Instance instances by query arguments

            Args:
                project      (Project) : parent Project instance.
                entity (Sequence|Shot) : parent Sequence instance.
                asset          (Asset) : Asset instance.
                name             (str) : Instance name.
                status           (str) : Instance status.
                id          (int/list) : Instance id(s).
                shotgun_id  (int/list) : Instance shotgun id(s).

            Returns:
                A list of Instance instances matching find arguments.
        '''
        query = cls.query(project=project, name=name, id=id, status=status, shotgun_id=shotgun_id)

        if entity:
            if entity.cls_name() == 'Sequence':
                field = cls.sequence_id
            elif entity.cls_name() == 'Shot':
                field = cls.shot_id
            else:
                raise TypeError('entity arg must be an Sequence or Shot class. Given {!r}'
                                .format(type(entity)))

            if isinstance(entity, (list, tuple)):
                query = query.filter(field.in_([e.id for e in entity]))
            else:
                query = query.filter(field == entity.id)

        if asset:
            cls.assert_isinstance(asset, 'Asset')
            query = query.filter(cls.asset_id == asset.id)

        return query.all()

    @classmethod
    def create(cls, name, project, entity, asset, status=None, shotgun_id=None):
        '''
        Create a Instance instance.

            Args:
                name            (str) : Instance name.
                project     (Project) : parent Project instance.
                sequence   (Sequence) : parent Sequence instance.
                cut           (Tuple) : (cut_in and cut_out) e.g. (1001,1002)
                status          (str) : Instance status.
                shotgun_id (int/list) : Instance shotgun id(s).

            Returns:
                New Instance Instance.

        '''
        cls.assert_isinstance(project, 'Project')
        cls.assert_isinstance(asset, 'Asset')

        (sequence, shot) = (None, None)
        if not isinstance(entity, Base):
            raise TypeError('entity arg must be an Entity class. Given {!r}'
                            .format(type(entity)))
        elif entity.cls_name() == 'Sequence':
            sequence = entity
        elif entity.cls_name() == 'Shot':
            shot = entity
        else:
            raise TypeError('entity arg must be a Sequence or Shot. Given {!r}'
                            .format(type(entity)))

        data = dict(name=name,
                    status=status,
                    project_id=project.id,
                    asset_id=asset.id,
                    sequence_id=getattr(sequence, 'id', None),
                    shot_id=getattr(shot, 'id', None),
                    shotgun_id=shotgun_id)

        return super(Instance, cls).create(**data)
