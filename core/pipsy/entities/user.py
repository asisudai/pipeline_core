'''User entity class'''

# imports
from sqlalchemy import (Table, Column, Integer, String, Enum, Index,
                        ForeignKey, UniqueConstraint)
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from .core import Base, ResultSet
from .project import Project


class User(Base):

    __table__ = Table('user', Base.metadata,

                      Column('id', Integer, primary_key=True),
                      Column('status', Enum('act', 'dis'), default='act', nullable=False),
                      Column('first_name', String(32), nullable=False),
                      Column('last_name', String(32), nullable=False),
                      Column('login', String(32), nullable=False),
                      Column('email', String(50), nullable=False),
                      Column('shotgun_id', Integer, nullable=True),

                      Index('ix_login', 'login'),
                      Index('ix_email', 'email'),
                      Index('ix_status', 'status'),
                      Index('ix_sg', 'shotgun_id'),

                      UniqueConstraint('login', name='uq_login'),
                      UniqueConstraint('email', name='uq_email'),
                      UniqueConstraint('shotgun_id', name='uq_sg')
                      )

    _userprojects = relationship('UserProject', backref='user', lazy='dynamic',
                                 cascade="all, delete-orphan")
    _usertasks = relationship('UserTask', backref='user', lazy='dynamic',
                              cascade="all, delete-orphan")

    def __repr__(self):
        return "{cls}(login='{login}', id={id})".format(cls=self.__class__.__name__,
                                                        login=self.login,
                                                        id=self.id)

    @hybrid_property
    def fullname(self):
        '''Return User fullname string as "{first_name} {last_name}".'''
        return '{} {}'.format(self.first_name, self.last_name)

    @fullname.expression
    def fullname(cls):
        return (cls.first_name + " " + cls.last_name)

    @property
    def projects(self):
        '''Returns Users instances assigned to Task'''
        query = Project.query()
        query = query.join(UserProject).filter(UserProject.user_id == self.id)
        return ResultSet(query.all())

    @projects.setter
    def projects(self, projects):
        '''
        Assign Users to Project.

            Supports operator assignment:
                self.projects = []
                self.projects += project
                self.projects -= project
                self.projects += [project]
                self.projects -= [project]
        '''
        UserProject.assign_projects_to_user(user=self, projects=projects)

    @property
    def tasks(self):
        '''Return Tasks user is assign to.'''
        from . task import Task
        return Task.find(user=self)

    @classmethod
    def find(cls, first_name=None, last_name=None, fullname=None, login=None,
             email=None, status=None, id=None, shotgun_id=None):
        '''
        Return User instances by query arguments

            Args:
                first_name      (str) : User first name.
                last_name       (str) : User last name.
                fullname        (str) : User fullname (hybrid).
                login           (str) : User login.
                email           (str) : User email.
                status        (Status): User status.
                id         (int/list) : User id(s)
                shotgun_id (int/list) : User shotgun id(s)

            Returns:
                A list of User instances matching find arguments.
        '''
        query = cls.query(id=id, status=status, shotgun_id=shotgun_id)

        if first_name:
            query = query.filter(cls.first_name == first_name)

        if last_name:
            query = query.filter(cls.last_name == last_name)

        if fullname:
            query = query.filter(cls.fullname == fullname)

        if login:
            query = query.filter(cls.login == login)

        if email:
            query = query.filter(cls.email == email)

        return query.all()

    @classmethod
    def create(cls, first_name, last_name, login, email, status=None, shotgun_id=None):
        '''
        Create a User instance.

            Args:
                first_name      (str) : User first name.
                last_name       (str) : User last name.
                login           (str) : User login.
                email           (str) : User email.
                status        (Status): User status.
                shotgun_id (int/list) : User shotgun id(s)

            Returns:
                New User Instance.

        '''
        data = dict(first_name=first_name,
                    last_name=last_name,
                    login=login,
                    email=email,
                    status=status,
                    shotgun_id=shotgun_id)

        return super(User, cls).create(**data)


class UserProject(Base):

    __table__ = Table('user_project', Base.metadata,
                      Column('user_id', Integer, ForeignKey(User.id),
                             primary_key=True, autoincrement=False),
                      Column('project_id', Integer, ForeignKey(Project.id),
                             primary_key=True, autoincrement=False),

                      Index('ix_user_id', 'user_id'),
                      Index('ix_project_id', 'project_id'),

                      UniqueConstraint('user_id', 'project_id',
                                       name='uq_user_project'),
                      )

    def __repr__(self):
        return "{cls}(user='{user}', project='{project}')".format(cls=self.__class__.__name__,
                                                                  user=self.user_id,
                                                                  project=self.project_id)

    @classmethod
    def assign_projects_to_user(cls, user, projects):
        '''
        Assign Projects to User.

           Args:
                user            (User): User to assignment.
                project (Project/list): Project(s) to assign.
        '''
        cls.assert_isinstances(projects, 'Project')
        cls.assert_isinstance(user, 'User')

        uprojects = UserProject.find(user=user)

        with user.session_context() as session:

            for uproj in uprojects:
                if uproj.user_id not in [p.id for p in projects]:
                    session.delete(uproj)

            for project in projects:
                if project.id not in [u.project_id for u in uprojects]:
                    new = UserProject(project_id=project.id, user_id=user.id)
                    session.add(new)

    @classmethod
    def find(cls, user=None, project=None):
        '''
        Return UserProject instances by query arguments

            Args:
                user       (User) : User instance.
                project (Project) : Project instance.

            Returns:
                A list of UserProject instances matching find arguments.
        '''
        query = cls.query()

        if user:
            query = query.filter(cls.user_id == user.id)

        if project:
            query = query.filter(cls.project_id == project.id)

        return query.all()

    @classmethod
    def create(cls, user, project):
        '''
        Create a UserProject instance.

            Args:
                user       (User) : User instance.
                project (Project) : Project instance.

            Returns:
                New UserProject Instance.
        '''
        cls.assert_isinstance(user, 'User')
        cls.assert_isinstance(project, 'Project')

        data = dict(user_id=user.id,
                    project_id=project.id)

        return super(UserProject, cls).create(**data)
