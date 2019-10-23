'''Sequence entity class'''

# imports
from sqlalchemy import (Table, Column, Integer, String, Enum, Index, SmallInteger,
                        ForeignKey, UniqueConstraint)
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from .core import Base, ResultSet
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
                      Column('cut_order', SmallInteger),
                      Column('description', String(255)),

                      Index('ix_proj_name', 'project_id', 'name', 'status'),
                      Index('ix_episode_name', 'episode_id', 'name', 'status'),
                      Index('ix_sg', 'shotgun_id'),

                      UniqueConstraint('project_id', 'episode_id_virtual', 'name',
                                       name='uq_proj_ep_name'),
                      UniqueConstraint('project_id', 'episode_id_virtual', 'basename',
                                       name='uq_proj_ep_basename'),
                      UniqueConstraint('shotgun_id', name='uq_sg')
                      )

    _shots = relationship('Shot', backref='sequence', lazy='dynamic',
                          order_by='Shot.name', cascade="all, delete-orphan")
    _instances = relationship('Instance', backref='sequence', lazy='dynamic',
                              order_by='Instance.name', cascade="all, delete-orphan")
    _publishgroups = relationship('PublishGroup', backref='sequence', lazy='dynamic',
                                  order_by='PublishGroup.id', cascade="all, delete-orphan")
    _tasks = relationship('Task', backref='sequence', lazy='dynamic',
                          order_by='Task.name', cascade="all, delete-orphan")

    @property
    def parent(self):
        '''
        Return Sequence parent entity, Episode if linked other wise to a Project.
        '''
        if self.episode_id:
            return self.episode
        else:
            return self.project

    @hybrid_property
    def fullname(self):
        '''
        Return Sequence fullname string.
        {episode.name}_{sequence.name} or {sequence.name}
        '''
        if self.episode_id:
            return '{}_{}'.format(self.episode.name, self.name)
        return '{}'.format(self.name)

    @property
    def instances(self):
        '''Return all Shot Instances active and disabled'''
        return [i for i in self._instances]

    @property
    def active_instances(self):
        '''Return active Sequence Instances'''
        instances = [i for i in self._instances if i.is_active()]
        return ResultSet(instances)

    @classmethod
    def find(cls, project=None, episode=False, name=None, status=None, id=None, shotgun_id=None):
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
        query = cls.query(project=project, name=name, id=id, status=status, shotgun_id=shotgun_id)

        if episode:
            query = query.filter(cls.episode_id == episode.id)

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
        cls.assert_isinstance(project, 'Project')

        if episode:
            cls.assert_isinstance(episode, 'Episode')

        data = dict(name=name,
                    basename=name,
                    status=status,
                    project_id=project.id,
                    episode_id=getattr(episode, 'id', None),
                    shotgun_id=shotgun_id)

        return super(Sequence, cls).create(**data)
