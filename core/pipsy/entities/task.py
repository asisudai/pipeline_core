'''Asset entity class'''

# imports
from sqlalchemy import (Table, Column, Integer, String, Enum, Index, ForeignKey,
                        UniqueConstraint, DateTime)
from sqlalchemy.orm import relationship
from .core import Base, ResultSet
from .project import Project
from .sequence import Sequence
from .shot import Shot
from .asset import Asset
from .user import User


class Task(Base):

    __table__ = Table('task', Base.metadata,

                      Column('id', Integer, primary_key=True),
                      Column('name', String(32), nullable=False),
                      Column('status', Enum('act', 'dis'), default='act', nullable=False),
                      Column('project_id', Integer, ForeignKey(Project.id), nullable=False),
                      Column('sequence_id', Integer, ForeignKey(Sequence.id)),
                      Column('shot_id', Integer, ForeignKey(Shot.id)),
                      Column('asset_id', Integer, ForeignKey(Asset.id)),
                      Column('shotgun_id', Integer, nullable=True),
                      Column('stage', String(32), nullable=False),
                      Column('description', String(255)),
                      Column('start_date', DateTime, default=None),
                      Column('end_date', DateTime, default=None),

                      Index('ix_proj_seq_stat', 'project_id', 'sequence_id', 'status'),
                      Index('ix_proj_shot_stat', 'project_id', 'shot_id', 'status'),
                      Index('ix_proj_asset_stat', 'project_id', 'asset_id', 'status'),
                      Index('ix_sg', 'shotgun_id'),

                      UniqueConstraint('shot_id', 'name', name='uq_shot_name'),
                      UniqueConstraint('sequence_id', 'name', name='uq_seq_name'),
                      UniqueConstraint('asset_id', 'name', name='uq_asset_name'),
                      UniqueConstraint('shotgun_id', name='uq_sg')
                      )

    _usertasks = relationship('UserTask', backref='task', lazy='dynamic',
                              cascade="all, delete-orphan")

    @property
    def parent(self):
        '''
        Return Task parent.
        Parent could be Sequence, Shot or Asset entity.
        '''
        if self.shot_id:
            return self.shot
        elif self.sequence_id:
            return self.sequence
        elif self.asset_id:
            return self.asset

    @property
    def users(self):
        '''Returns Users instances assigned to Task'''
        query = User.query()
        query = query.join(UserTask).filter(UserTask.task_id == self.id)
        return ResultSet(query.all())

    @users.setter
    def users(self, users):
        '''
        Assign Users to Task.

            Supports operator assignment:
                self.users = []
                self.users += user
                self.users -= user
                self.users += [user]
                self.users -= [user]
        '''
        # TODO: replce with entity's specific session context
        # from ..db import session_context
        utasks = UserTask.find(task=self)

        with self.session_context() as session:

            for utask in utasks:
                if utask.user_id not in [u.id for u in users]:
                    session.delete(utask)

            for user in users:
                if user.id not in [u.user_id for u in utasks]:
                    new = UserTask(user_id=user.id, task_id=self.id)
                    session.add(new)

    @classmethod
    def find(cls, project=None, entity=None, name=None, stage=None, status=None,
             user=None, start_date=None, end_date=None, id=None, shotgun_id=None):
        '''
        Return Task instances by query arguments

            Args:
                project     (Project) : parent Project instance.
                entity       (Entity) : parent Shot, Sequence or Asset instance.
                name            (str) : Task name.
                stage           (str) : Task stage.
                user           (user) : User assignment.
                start_date (datetime) : start date. defaults to None.
                end_date   (datetime) : end date. defaults to None.
                status          (str) : Task status.
                id         (int/list) : Task id(s).
                shotgun_id (int/list) : Task shotgun id(s).

            Returns:
                A list of Task instances matching find arguments.
        '''
        query = cls.query(project=project, name=name, id=id, status=status, shotgun_id=shotgun_id)

        if entity:
            if entity.cls_name() == 'Sequence':
                field = cls.sequence_id
            elif entity.cls_name() == 'Shot':
                field = cls.shot_id
            elif entity.cls_name() == 'Asset':
                field = cls.asset_id
            else:
                raise TypeError('entity arg must be an Sequence or Shot or Asset class. Given {!r}'
                                .format(type(entity)))

            if isinstance(entity, (list, tuple)):
                query = query.filter(field.in_([e.id for e in entity]))
            else:
                query = query.filter(field == entity.id)

        if user:
            query = query.join(UserTask).filter(UserTask.user_id == user.id)

        if stage:
            query = query.filter(cls.stage == stage)

        if start_date:
            query = query.filter(cls.start_date == start_date)

        if end_date:
            query = query.filter(cls.end_date == end_date)

        return query.all()

    @classmethod
    def create(cls, name, project, entity, stage, start_date=None, end_date=None,
               status=None, shotgun_id=None):
        '''
        Create a Task instance.

            Args:
                name            (str) : Task name.
                project     (Project) : parent Project instance.
                entity       (Entity) : parent Shot, Sequence or Asset instance.
                stage           (str) : Task stage.
                status          (str) : Task status.
                id         (int/list) : Task id(s).
                shotgun_id (int/list) : Task shotgun id(s).

            Returns:
                New Task Instance.

        '''
        if not isinstance(project, Base) or not project.cls_name() == 'Project':
            raise TypeError('project arg expected Project entity. Given {!r}'
                            .format(type(project)))

        (sequence, shot, asset) = (None, None, None)
        if not isinstance(entity, Base):
            raise TypeError('entity arg must be an Entity class. Given {!r}'
                            .format(type(entity)))
        elif entity.cls_name() == 'Sequence':
            sequence = entity
        elif entity.cls_name() == 'Shot':
            shot = entity
        elif entity.cls_name() == 'Asset':
            asset = entity
        else:
            raise TypeError('entity arg must be a Sequence or Shot or Asset. Given {!r}'
                            .format(type(entity)))

        data = dict(name=name,
                    project_id=project.id,
                    sequence_id=getattr(sequence, 'id', None),
                    shot_id=getattr(shot, 'id', None),
                    asset_id=getattr(asset, 'id', None),
                    stage=stage,
                    start_date=start_date,
                    end_date=end_date,
                    status=status,
                    shotgun_id=shotgun_id)

        return super(Task, cls).create(**data)


class UserTask(Base):

    __table__ = Table('user_task', Base.metadata,
                      Column('user_id', Integer, ForeignKey(User.id),
                             primary_key=True, autoincrement=False),
                      Column('task_id', Integer, ForeignKey(Task.id),
                             primary_key=True, autoincrement=False),

                      Index('ix_user_id', 'user_id'),
                      Index('ix_task_id', 'task_id'),

                      UniqueConstraint('user_id', 'task_id', name='uq_user_task'),
                      )

    def __repr__(self):
        return "{cls}(user='{user}', task='{task}')".format(cls =self.__class__.__name__,
                                                            task=self.task_id,
                                                            user=self.user_id)

    @classmethod
    def find(cls, user=None, task=None):
        '''
        Return UserTask instances by query arguments

            Args:
                user     (User) : User instance.
                task     (Task) : Task instance.

            Returns:
                A list of UserTask instances matching find arguments.
        '''
        query = cls.query()

        if user:
            query = query.filter(cls.user_id == user.id)

        if task:
            query = query.filter(cls.task_id == task.id)

        return query.all()

    @classmethod
    def create(cls, user, task):
        '''
        Create a Task instance.

            Args:
                user     (User) : User instance.
                task     (Task) : Task instance.

            Returns:
                New UserTask Instance.
        '''
        if not isinstance(user, Base) or not user.cls_name() == 'User':
            raise TypeError('user arg expected User entity. Given {!r}'
                            .format(type(user)))

        if not isinstance(task, Base) or not task.cls_name() == 'Task':
            raise TypeError('task arg expected Task entity. Given {!r}'
                            .format(type(task)))

        data = dict(user_id = user.id,
                    task_id = task.id)

        return super(UserTask, cls).create(**data)
