'''PublishGroup entity class'''

# imports
from sqlalchemy import (Table, Column, Integer, Enum, Index, DateTime, Boolean,
                        ForeignKey, UniqueConstraint)
from .core import Base
from .project import Project
from .sequence import Sequence
from .shot import Shot
from .asset import Asset
from .instance import Instance
from .publishkind import PublishKind


class PublishGroup(Base):

    __table__ = Table('publishgroup', Base.metadata,
                      Column('id', Integer, primary_key=True),
                      Column('status', Enum('act', 'dis'), default='act', nullable=False),
                      Column('kind_id', Integer, ForeignKey(PublishKind.id), nullable=False),
                      Column('lock', Boolean, default=False),
                      Column('checkout_user_id', Integer, default=None),
                      Column('checkout_date', DateTime, default=None),
                      Column('project_id', Integer, ForeignKey(Project.id), nullable=False),
                      Column('sequence_id', Integer, ForeignKey(Sequence.id)),
                      Column('shot_id', Integer, ForeignKey(Shot.id)),
                      Column('instance_id', Integer, ForeignKey(Instance.id)),
                      Column('asset_id', Integer, ForeignKey(Asset.id)),

                      Index('ix_project_kind', 'project_id', 'kind_id'),
                      Index('ix_project_seq_kind', 'project_id', 'sequence_id', 'kind_id'),
                      Index('ix_project_asset_kind', 'project_id', 'asset_id', 'kind_id'),
                      Index('ix_project_shot_kind', 'project_id', 'shot_id', 'kind_id'),
                      Index('ix_project_instance_kind', 'project_id', 'instance_id', 'kind_id'),

                      UniqueConstraint('sequence_id', 'kind_id', name='uq_sequence_kind'),
                      UniqueConstraint('shot_id', 'kind_id', name='uq_shot_kind'),
                      UniqueConstraint('asset_id', 'kind_id', name='uq_asset_kind'),
                      UniqueConstraint('instance_id', 'kind_id', name='uq_instance_kind')
                      )

    def __repr__(self):
        return "{cls}(id={id})".format(cls=self.__class__.__name__, id=self.id)

    @property
    def parent(self):
        '''
        Return PublishGroup parent entity.
        Parent could be Sequence, Shot, Instance or Asset entity.
        '''
        if self.instance_id:
            return self.instance
        elif self.shot_id:
            return self.shot
        elif self.sequence_id:
            return self.sequence
        elif self.asset_id:
            return self.asset

    @classmethod
    def find(cls, project=None, entity=None, kind=None, lock=None, status=None, id=None):
        '''
        Return PublishGroup instances by query arguments

            Args:
                project      (Project) : parent Project instance.
                entity   (Sequence|Shot|Asset|instance) : PublishGroup parent entity.
                kind     (PublishKind) : PublishGroup kind.
                lock     (bool)        : PublishGroup lock state.
                status           (str) : PublishGroup status.
                id          (int/list) : PublishGroup id(s).

            Returns:
                A list of PublishGroup instances matching find arguments.
        '''
        query = cls.query(project=project, id=id, status=status)

        if entity:
            cls.assert_isinstance(entity, ('Sequence', 'Shot', 'Asset', 'Instance'))
            if entity.cls_name() == 'Sequence':
                field = cls.sequence_id
            elif entity.cls_name() == 'Shot':
                field = cls.shot_id
            elif entity.cls_name() == 'Asset':
                field = cls.asset_id
            elif entity.cls_name() == 'Instance':
                field = cls.instance_id

            if isinstance(entity, (list, tuple)):
                query = query.filter(field.in_([e.id for e in entity]))
            else:
                query = query.filter(field == entity.id)

        if kind:
            cls.assert_isinstance(kind, 'PublishKind')
            query = query.filter(cls.kind_id == kind.id)

        if lock:
            query = query.filter(cls.lock == lock)

        return query.all()

    @classmethod
    def create(cls, project, entity, kind, lock=None, status=None):
        '''
        Create a PublishGroup instance.

            Args:
                project      (Project) : parent Project instance.
                entity   (Sequence|Shot|Asset|instance) : PublishGroup parent entity.
                kind     (PublishKind) : PublishGroup kind.
                lock     (bool)        : PublishGroup lock state.
                status           (str) : PublishGroup status.
                id          (int/list) : PublishGroup id(s).

            Returns:
                New PublishGroup Instance.
        '''
        cls.assert_isinstance(project, 'Project')
        cls.assert_isinstance(entity, ('Sequence', 'Shot', 'Asset', 'Instance'))
        cls.assert_isinstance(kind, 'PublishKind')

        (sequence_id, shot_id, asset_id, instance_id) = (None, None, None, None)
        if entity.cls_name() == 'Sequence':
            sequence_id = entity.id
        elif entity.cls_name() == 'Shot':
            shot_id = entity.id
        elif entity.cls_name() == 'Asset':
            asset_id = entity.id
        elif entity.cls_name() == 'Instance':
            instance_id = entity.id

        data = dict(project_id  = project.id,
                    sequence_id = sequence_id,
                    shot_id     = shot_id,
                    instance_id = instance_id,
                    asset_id    = asset_id,
                    kind_id     = kind.id,
                    lock        = lock,
                    status      = status)

        return super(PublishGroup, cls).create(**data)
