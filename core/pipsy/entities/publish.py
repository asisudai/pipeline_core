'''Publish entity class'''

# imports
from sqlalchemy import (Table, Column, Integer, Enum, Index, DateTime, DECIMAL,
                        String, SmallInteger, ForeignKey, UniqueConstraint)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .core import Base
from ..core.pythonx import string_types
from .project import Project
from .user import User
from .task import Task
from .publishgroup import PublishGroup
from .publishkind import PublishKind


class Publish(Base):

    __table__ = Table('publish', Base.metadata,
                      Column('id', Integer, primary_key=True),
                      Column('status', Enum('act', 'dis'), default='act', nullable=False),
                      Column('root', String(512), nullable=True),
                      Column('path', String(512), nullable=True),
                      Column('version', SmallInteger, nullable=False),
                      Column('project_id', Integer, ForeignKey(Project.id), nullable=False),
                      Column('publishgroup_id', Integer, ForeignKey(PublishGroup.id),
                             nullable=False),
                      Column('publishkind_id', Integer, ForeignKey(PublishKind.id), nullable=False),
                      Column('user_id', Integer, ForeignKey(User.id), nullable=False),
                      Column('task_id', Integer, ForeignKey(Task.id)),
                      Column('diskspace', DECIMAL(10, 3)),  # TODO: make use of this
                      Column('created', DateTime(timezone=True), server_default=func.now()),
                      Column('updated', DateTime(timezone=True), onupdate=func.now()),
                      Column('description', String(512)),

                      Index('ix_project_group_kind', 'project_id', 'publishgroup_id',
                            'publishkind_id'),
                      Index('ix_project_kind_root', 'project_id', 'publishkind_id', 'root'),
                      Index('ix_project_task', 'project_id', 'task_id'),
                      Index('ix_project_user', 'project_id', 'user_id'),

                      UniqueConstraint('publishgroup_id', 'publishkind_id', 'version',
                                       name="uq_group_kind_version"),
                      UniqueConstraint('publishgroup_id', 'publishkind_id', 'root',
                                       name="uq_group_kind_root"),
                      )

    _publishmetadata = relationship('PublishMetadata', backref='publish', lazy='dynamic',
                                    cascade="all, delete-orphan")

    def __repr__(self):
        return "{cls}(id={id})".format(cls=self.__class__.__name__, id=self.id)

    @property
    def parent(self):
        '''
        Return Publish parent entity.
        Parent could be Sequence, Shot, Instance or Asset entity.
        '''
        return self.publishgroup.parent

    @property
    def metadata(self):
        '''
        Return Publish metadata from PublishMetadata entity.
        '''
        _metas = [m for m in self._publishmetadata]
        return _metas[0].metadata if _metas else None

    @metadata.setter
    def metadata(self, data):
        '''
        Set Publish metadata into PublishMetadata entity.
        '''
        from . import PublishMetadata
        PublishMetadata.set_metadata(self, data)

    @classmethod
    def find(cls, project=None, publishgroup=None, publishkind=None,
             version=None, root=None, path=None, user=None, status=None, id=None):
        '''
        Return Publish instances by query arguments

            Args:
                project           (Project) : parent Project instance.
                publishgroup (PublishGroup) : PublishGroup parent.
                publishkind   (PublishKind) : PublishKind link.
                version               (int) : Publish version number.
                root                  (str) : Publish root in filesystem.
                path                  (str) : Publish path in filesystem.
                user                 (User) : Publish user instance.
                status                (str) : Publish status.
                id               (int/list) : Publish id(s).

            Returns:
                A list of Publish instances matching find arguments.
        '''
        query = cls.query(project=project, id=id, status=status)

        if publishgroup:
            cls.assert_isinstance(publishgroup, 'PublishGroup')
            query = query.filter(cls.publishgroup_id == publishgroup.id)

        if publishkind:
            cls.assert_isinstance(publishkind, 'PublishKind')
            query = query.filter(cls.publishkind_id == publishkind.id)

        if user:
            cls.assert_isinstance(user, 'User')
            query = query.filter(cls.user_id == user.id)

        if version:
            assert isinstance(version, int), ('version arg must be int. Given {}'
                                              .format(type(version)))
            query = query.filter(cls.version == version)

        if root:
            assert isinstance(root, string_types), ('root arg must be string. Given {}'
                                                    .format(type(root)))
            query = query.filter(cls.root == root)

        if path:
            assert isinstance(path, string_types), ('path arg must be string. Given {}'
                                                    .format(type(path)))
            query = query.filter(cls.path == path)

        return query.all()

    @classmethod
    def create(cls, project, publishgroup, publishkind, user, version, root,
               path=None, description=None, status=None):
        '''
        Create a Publish instance.

            Args:
                project           (Project) : parent Project instance.
                publishgroup (PublishGroup) : PublishGroup parent.
                publishkind   (PublishKind) : PublishKind link.
                user                 (User) : Publish User instance.
                version               (int) : Publish version number.
                root                  (str) : Publish root in filesystem.
                path                  (str) : Publish path in filesystem.
                status                (str) : Publish status.

            Returns:
                New Publish Instance.
        '''
        cls.assert_isinstance(project, 'Project')
        cls.assert_isinstance(publishgroup, 'PublishGroup')
        cls.assert_isinstance(publishkind, 'PublishKind')
        cls.assert_isinstance(user, 'User')
        assert isinstance(version, int), ('version arg must be int. Given {}'
                                          .format(type(version)))
        assert isinstance(root, string_types), ('root arg must be string. Given {}'
                                                .format(type(root)))

        data = dict(project_id      = project.id,
                    publishgroup_id = publishgroup.id,
                    publishkind_id  = publishkind.id,
                    user_id         = user.id,
                    version         = version,
                    root            = root,
                    path            = path,
                    description     = description,
                    status          = status)

        return super(Publish, cls).create(**data)
