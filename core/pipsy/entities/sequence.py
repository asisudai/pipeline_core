'''Sequence entity class'''

# imports
from sqlalchemy import (Table, Column, Integer, String, Enum, Index,
                        ForeignKey, UniqueConstraint)
# from sqlalchemy.orm import relationship
from .core import Base
from .project import Project
from .episode import Episode


def calc_episode(context):
    '''
    Update episode_id_virtual with the episode_id as a none primary_key. A workaround
    for UniqueConstraint issue with NULL fields.
    '''
    # Generated column for episode_id_virtual to support unique constraint with NULL episodes
    # Column('episode_id_virtual', Integer, FetchedValue(), nullable=False),
    # session.bind.execute("ALTER TABLE `unittest`.`sequence` CHANGE COLUMN `episode_id_virtual`
    # `episode_id_virtual` INT(11) GENERATED ALWAYS AS(IFNULL(`episode_id`, 0)) STORED")
    ep_id = context.get_current_parameters()['episode_id']
    return ep_id or 0


class Sequence(Base):

    __table__ = Table('sequence', Base.metadata,
                      Column('id', Integer, primary_key=True),
                      Column('name', String(32), nullable=False),
                      Column('basename', String(32), nullable=False),
                      Column('status', Enum('act', 'dis'), default='act', nullable=False),
                      Column('project_id', Integer, ForeignKey(Project.id), nullable=False),
                      Column('episode_id', Integer, ForeignKey(Episode.id)),
                      Column('episode_id_virtual', Integer,
                             default=calc_episode, onupdate=calc_episode),
                      Column('shotgun_id', Integer),

                      Index('ix_proj_name', 'project_id', 'name', 'status'),
                      Index('ix_episode_name', 'episode_id', 'name', 'status'),
                      Index('ix_sg', 'shotgun_id'),

                      UniqueConstraint('project_id', 'episode_id_virtual', 'name',
                                       name='uq_proj_ep_name'),
                      UniqueConstraint('project_id', 'episode_id_virtual', 'basename',
                                       name='uq_proj_ep_basename'),
                      UniqueConstraint('shotgun_id', name='uq_sg')
                      )

    @classmethod
    def find(cls, project=None, episode=None, name=None, status=None, id=None, shotgun_id=None):
        '''
        Return Sequence instances by query arguments

            Args:
                project     (Project) : parent Project instance.
                episode     (Episode) : parent Episode instance (optional).
                name            (str) : Episode name.
                status          (str) : Episode status.
                id         (int/list) : Episode id(s).
                shotgun_id (int/list) : Epsiode shotgun id(s).

            Returns:
                A list of Sequence instances matching find arguments.
        '''
        query = cls.query(id=id, status=status, shotgun_id=shotgun_id)

        if project:
            query = query.filter(cls.project_id == project.id)

        if episode:
            query = query.filter(cls.episode_id == episode.id)

        if name:
            query = query.filter(cls.name == name)

        return query.all()

    @classmethod
    def create(cls, name, project, episode=None, status=None, shotgun_id=None):
        '''
        Create a Sequence instance.

            Args:
                name            (str) : Sequence name.
                project     (Project) : parent Project instance.
                episode     (Episode) : parent Episode instance.
                status          (str) : Sequence status.
                shotgun_id (int/list) : Sequence shotgun id(s).

            Returns:
                New Sequence Instance.

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
                    episode_id=getattr(episode, 'id', None),
                    shotgun_id=shotgun_id)

        return super(Sequence, cls).create(**data)
