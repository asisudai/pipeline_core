'''PublishKind entity class'''

# imports
from sqlalchemy import (Table, Column, Integer, String, Enum, Index, UniqueConstraint)
from sqlalchemy.orm import relationship
from .core import Base


def calc_subkind(context):
    '''
    Update subkind_virtual with the episode_id as a none primary_key. A workaround
    for UniqueConstraint issue with NULL fields.
    '''
    # Generated column for subkind_virtual to support unique constraint with NULL episodes
    # Column('subkind_virtual', Integer, FetchedValue(), nullable=False),
    # session.bind.execute("ALTER TABLE `unittest`.`publishkind` CHANGE COLUMN `subkind_virtual`
    # `subkind_virtual` INT(11) GENERATED ALWAYS AS(IFNULL(`subkind`, 0)) STORED")
    subkind = context.get_current_parameters()['subkind']
    return subkind or 0


class PublishKind(Base):

    __table__ = Table('publishkind', Base.metadata,
                      Column('id', Integer, primary_key=True),
                      Column('name', String(32), nullable=False),
                      Column('nicename', String(32), nullable=False),
                      Column('status', Enum('act', 'dis'), default='act', nullable=False),
                      Column('kind', String(12), nullable=False),
                      Column('subkind', String(12)),
                      Column('subkind_virtual', String(12),
                             default=calc_subkind, onupdate=calc_subkind),
                      Column('lod', String(12)),
                      Column('description', String(255)),

                      Index('ix_name', 'name'),
                      Index('ix_nicename', 'nicename'),
                      Index('ix_kind_subkind_lod', 'kind', 'subkind', 'lod'),

                      UniqueConstraint('name', name='uq_name'),
                      UniqueConstraint('nicename', name='uq_nicename'),
                      UniqueConstraint('kind', 'subkind_virtual', 'lod', name='uq_kind_sub_lod')
                      )

    _publishgroups = relationship('PublishGroup', backref='kind', lazy='dynamic',
                                  order_by='PublishGroup.id', cascade="all, delete-orphan")

    @classmethod
    def find(cls, name=None, nicename=None, kind=None, subkind=None, lod=None,
             status=None, id=None):
        '''
        Return PublishKind instances by query arguments

            Args:
                name     (str) : PublishKind name.
                nicename (str) : PublishKind nicename.
                kind     (str) : PublishKind kind.
                subkind  (str) : PublishKind subkind.
                lod      (str) : PublishKind level of detail.
                status   (str) : PublishKind status.
                id  (int/list) : PublishKind id(s).

            Returns:
                A list of PublishKind instances matching find arguments.
        '''
        query = cls.query(name=name, id=id, status=status)

        if nicename:
            query = query.filter(cls.nicename == nicename)

        if kind:
            query = query.filter(cls.kind == kind)

        if subkind:
            query = query.filter(cls.subkind == subkind)

        if lod:
            query = query.filter(cls.lod == lod)

        return query.all()

    @classmethod
    def create(cls, name, nicename, kind, subkind=None, lod=None, description=None, status=None):
        '''
        Create a PublishKind instance.

            Args:
                name       (str) : PublishKind name.
                nicename   (str) : PublishKind nicename.
                kind       (str) : PublishKind kind.
                subkind    (str) : PublishKind subkind.
                lod        (str) : PublishKind level of detail.
                description (str): PublishKind description.
                status     (str) : PublishKind status.

            Returns:
                New PublishKind Instance.

        '''
        data = dict(name=name,
                    nicename=nicename,
                    kind=kind,
                    subkind=subkind,
                    lod=lod,
                    description=description,
                    status=status)

        return super(PublishKind, cls).create(**data)
