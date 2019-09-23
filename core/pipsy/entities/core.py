#!/usr/bin/env python
'''Entities Base Class'''

# imports
import traceback
import time
from contextlib import contextmanager
from sqlalchemy import event, inspect, MetaData, DateTime, String, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.types import TypeDecorator
from sqlalchemy.orm.util import identity_key
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from sqlalchemy.exc import DataError, IntegrityError, InvalidRequestError
import star.db
from star.core import logging, dirmap

LOG = logging.getLogger(__name__, level=logging.INFO)


class BaseEntity(object):
    '''SCL entities base class'''

    def __init__(self, **columns):
        self._columns = columns

        for key, value in columns.iteritems():
            setattr(self, key, value)

    def __repr__(self):
        return "{cls}(id={id})".format(cls=self.__class__.__name__,
                                       id=self.id)

    def __ne__(self, other):
        return not self == other

    def __eq__(self, other):
        return (self.__class__ == other.__class__) and \
               (identity_key(instance=self) == identity_key(instance=other))

    def __hash__(self):
        key = identity_key(instance=self)
        if len(key) == 1:
            key = key[0]

        return hash((self.__class__, key))

    def __iter__(self):
        def convert_datetime(value):
            if value:
                return value.strftime("%Y-%m-%d %H:%M:%S")

        for col in self.__table__.columns:
            if isinstance(col.type, DateTime):
                value = convert_datetime(getattr(self, col.name))
            else:
                value = getattr(self, col.name)

            yield(col.name, value)

    def __getstate__(self):
        '''pickle.dumps to serialized/Deserializer entity'''
        result = dict()
        for key in self.__table__.columns.keys():
            result[key] = getattr(self, key)

        # Need to include this. need to dig deeper to know why exactly.
        result['_sa_instance_state'] = self._sa_instance_state
        return result
        # result = dict(cls_name=self.cls_name, id_=self.id)
        # return result

    def __setstate__(self, state):
        '''pickle.loads entity'''
        try:
            self._connect().session.add(self)
        except InvalidRequestError:
            self._connect().session.merge(self)
        self._columns = state

        for key, value in state.items():
            setattr(self, key, value)

        # from star.entities import find_entity
        # entity = find_entity(**state)
        # self._sa_instance_state = entity._sa_instance_state
        # self._connect().session.merge(self)
        # for key in self.__table__.columns.keys():
        #     setattr(self, key, getattr(entity, key))

    def pickle_dumps(self):
        '''Serialize entity using jalapeno'''
        from ..core import jalapeno
        return jalapeno.dumps(self)

    @classmethod
    def pickle_loads(cls, jstring):
        '''Deserialize entity using jalapeno'''
        from ..core import jalapeno
        entity = jalapeno.loads(jstring)
        return cls._connect().session.merge(entity)

    @property
    def cls_name(self):
        '''Returns entity's class name'''
        return self.__class__.__name__

    @property
    def breadcrumb(self):
        '''
        breadcrumb representation
        e.g ark/0100/0010 or ark/char/gilbert
        '''
        path = self.name
        parent = self.parent

        while parent:
            path = "{}/{}".format(parent.name, path)
            parent = getattr(parent, 'parent', None)

        return path

    @classmethod
    def find(cls, **kwargs):
        '''find() must be override by subclass'''
        raise NotImplementedError(
            'find() needs to be override by subclass "{}"'.format(cls.__name__))

    @classmethod
    def find_one(cls, **kwargs):
        '''wrapper of find() that return a single result'''
        result = cls.find(**kwargs)

        if not result:
            raise NoResultFound(
                "No {} found for query:{}".format(cls.__name__, kwargs))
        elif len(result) > 1:
            raise MultipleResultsFound(
                "More than one {} found for query:{}".format(cls.__name__, kwargs))
        else:
            return result[0]

    @classmethod
    def findby_id(cls, id):
        '''Return an instance based on given id
        Will error out if no result found.

        args:
            id (int): The id to search by.
        '''
        try:
            return cls._connect().query(cls).filter_by(id=id).one()
        except NoResultFound:
            raise NoResultFound(
                "No {} found for id:{}".format(cls.__name__, id))

    @classmethod
    def available_status(cls):
        '''
        Return a list of all available status.
        '''
        column = cls.__table__.columns.get('status')
        return sorted(column.type.__dict__['enums'])

    @classmethod
    def findby_ids(cls, ids):
        '''Return instances based on given ids.
        Will return an empty list if none found.

        args:
            ids (list): The ids to search by.
        '''
        return cls._connect().query(cls).filter(cls.id.in_(ids)).all()

    @classmethod
    def create(cls, **kw):
        '''
        Create a new entity in the database.
        Will do SQL insert call to the db, making this entity permanently available.
        '''
        session = None
        try:
            session = cls._connect()
            session.start_transaction()

            # Connect to db and add new instance
            new = cls(**kw)
            session.add(new)
            session.flush()
            session.commit_transaction()

            return new

        except (DataError, IntegrityError) as err:
            LOG.fatal('{} {}'.format(err.__class__.__name__, err.message))
            LOG.fatal('{} {}'.format(err.statement, err.params))
            if session:
                session.rollback_transaction()
            raise

        except Exception:
            if session:
                session.rollback_transaction()
            raise

    @classmethod
    def default_status(cls):
        '''Returns the default status used for this entity.
        '''
        column = cls.__table__.columns.get('status')
        return column.default.arg

    @classmethod
    def disabled_status(cls):
        '''Returns the disable status used for this entity.
        '''
        return cls._disabled_statuses()[0]

    @classmethod
    def _disabled_statuses(cls):
        '''Returns a tuple of disabled status.
        Used by find() functions to filter out disabled/omitted entities.
        Some entities might need to override this, if are unique.
        '''
        return ('dis', 'omt')

    @contextmanager
    def session_context(self):
        '''Provide a transactional scope around a series of operations.'''
        session = inspect(self).session
        session.begin(subtransactions=True)
        try:
            yield session
        except Exception:
            if session.transaction or session.transaction.is_active:
                session.rollback()
            raise
        else:
            session.commit()

    @classmethod
    def _connect(self):
        '''
        Returns db connection.
        Better to use self.session_context with instance.
        '''
        return star.db.connect_pipeline()


# Register BaseEntity with sqlAlchemy declarative base.
metadata = MetaData()
Base = declarative_base(cls=BaseEntity, metadata=metadata)


class ShotgunMixin(object):
    '''
    Shotgun Mixin class.
    Used for entities which are both in local-db and sg.
    '''

    @classmethod
    def findby_shotgun_id(cls, shotgun_id):
        '''
        Return entity by it's shotgun_id.

        args:
            shotgun_id (int) : shotgun id.
        '''
        if not shotgun_id:
            raise ValueError("shotgun_id argument is required.")

        return cls.find_one(shotgun_id=shotgun_id)

    @classmethod
    def findby_shotgun_ids(cls, shotgun_ids):
        '''
        Return entities by their shotgun_ids.

        args:
            shotgun_ids (list) : a list of shotgun ids.
        '''
        if not shotgun_ids:
            raise ValueError("shotgun_ids argument is required.")
        elif type(shotgun_ids) not in (list, tuple):
            raise TypeError("shotgun_ids must be a list or tuple.")

        return cls.find(shotgun_id=shotgun_ids)

    @classmethod
    def shotgun_class(cls):
        '''Returns a Shotgun class string name'''
        # TODO: rename this function or ref-factor, duplicate of shotgun_cls_type.
        from ..shotgun.sync import shotgun_class_from_local
        return shotgun_class_from_local(cls)

    @property
    def shotgun_cls_type(self):
        '''Returns entity's shotgun class type.'''
        return self.shotgun_class()

    @property
    def shotgun_key(self):
        '''Returns entity's shotgun ID key (type/id).'''
        if self.shotgun_id is None:
            raise ValueError("This entity {} has no shotgun_id.".format(self))

        return AttributeDict({"type": self.shotgun_cls_type, "id": self.shotgun_id})

    @property
    def shotgun_url(self):
        '''Returns entity's shotgun url.'''
        # TODO: duplicate of Shotgun classmethod no?
        from ..shotgun import SERVER_URL
        return "{}/detail/{}/{}".format(SERVER_URL, self.shotgun_cls_type, self.shotgun_id)

    @property
    def shotgun_thumbnail_url(self):
        '''Returns entity's thumbnail shotgun url'''
        from ..shotgun import SERVER_URL
        return "{}/thumbnail/{}/{}".format(SERVER_URL, self.shotgun_cls_type, self.shotgun_id)

    def update_thumbnail(self, thumbnail):
        '''Updates the entity's thumbnail'''
        self._shotgun_connect().upload_thumbnail(
            self.shotgun_cls_type, self.shotgun_id, thumbnail)

    def update_shotgun(self, data):
        '''
        Update the self on the shotgun side with given data.
        Used to update Shotgun fields that we don't sync/map between Local&Shotgun.
        '''
        # TODO : do we still need this function? what's it's good for?
        from ..shotgun import connect
        connect().update(self.shotgun_cls_type, self.shotgun_id, data)

    @classmethod
    def _shotgun_connect(cls):
        from ..shotgun import connect
        return connect()

    def shotgun_thumbnail(self, forceRefresh=False):
        '''
        Return entity's thumbnail.
        '''
        raise NotImplemented('Not there yet')

    def sync_to_shotgun(self, entity_id=None, force=False):
        from ..shotgun import sync
        sync.sync_to_shotgun(self, shotgun_id=entity_id, force=force)

    def sync_from_shotgun(self, shotgun_id=None):
        from ..shotgun import sync
        sync.sync_from_shotgun(self, shotgun_id=shotgun_id)
        session = inspect(self).session

        if session:
            # session = self._connect()
            # session.add(self)
            session.refresh(self)

    def _receive_attribute_instrument(self, etype, key, new_value, old_value):
        '''called when sqlalchemy event is trigger (attribute changed)'''

        # Skip shotgun_id. handled elsewhere in shotgun.sync.core
        if key == 'shotgun_id':
            return

        # Skip if not persistent (just been created and haven't been committed).
        # this will be handled elsewhere.
        # if not inspect(self).persistent:
            # return

        session = self._connect().session

        if not hasattr(session, "_entities_to_sg_sync"):
            session._entities_to_sg_sync = set()

        # Add to sync
        session._entities_to_sg_sync.add(self)
        LOG.debug("_entities_to_sg_sync : {}".format(
            session._entities_to_sg_sync))

    @classmethod
    def shotgun_fields(cls):
        '''
        A list of shotgun fields (columns) that this entity needs.
        '''
        return []


class ShotgunJoinMixin(object):
    '''
    Shotgun Join Mixin class.
    Used for join table entities e.g UserTask.
    '''

    def _receive_attribute_instrument(self, etype, key, new_value, old_value):
        if hasattr(self, "left_parent") and isinstance(self.left_parent, ShotgunMixin):
            self.left_parent._receive_attribute_instrument(
                etype, key, new_value, old_value)

        if hasattr(self, "right_parent") and isinstance(self.right_parent, ShotgunMixin):
            self.right_parent._receive_attribute_instrument(
                etype, key, new_value, old_value)


class AttributeDict(dict):
    '''Python magic. magic.'''
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__

    def __hash__(self):
        return hash(tuple(sorted(self.items())))


class JSONType(TypeDecorator):
    impl = JSON

    # call when result/string are going IN to the table.
    # paths string going IN as linux paths.
    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        return value

    # call when result/string are going OUT to the table.
    # paths string going OUT as the current OS paths.
    def process_result_value(self, value, dialect):
        if value is None:
            return AttributeDict()
        return AttributeDict(value)


class DirmapType(TypeDecorator):
    impl = String

    # call when result/string are going IN to the table.
    # paths string going IN as linux paths.
    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        return dirmap.map_linux(value)

    # call when result/string are going OUT to the table.
    # paths string going OUT as the current OS paths.
    def process_result_value(self, value, dialect):
        if value is None:
            return value
        return dirmap.DirmapString(value)


class FormattedString(TypeDecorator):
    '''
    Format strings coming in and out of the database
    Main issue is limit/cut strings coming in to fit field length.
    '''
    impl = String

    # string value going IN the database.
    def process_bind_param(self, value, dialect):
        if value is None:
            return value

        if len(value) > self.impl.length:
            value = value[:self.impl.length]

        return value

    # string value going OUT the database.
    def process_result_value(self, value, dialect):
        if value is None:
            return value

        return value.encode('utf-8')


@event.listens_for(ShotgunMixin, 'attribute_instrument')
@event.listens_for(ShotgunJoinMixin, 'attribute_instrument')
def receive_attribute_instrument(cls, key, inst):
    """listen for the 'attribute_instrument' event"""

    def append(instance, value, initiator):
        instance._receive_attribute_instrument("append", key, value, None)

    def remove(instance, value, initiator):
        instance._receive_attribute_instrument("remove", key, value, None)

    def set_(instance, value, oldvalue, initiator):
        instance._receive_attribute_instrument("set", key, value, oldvalue)

    event.listen(inst, 'append', append)
    event.listen(inst, 'remove', remove)
    event.listen(inst, 'set', set_)


# @event.listens_for(ShotgunJoinMixin, 'instrument_class', propagate=True)
@event.listens_for(ShotgunMixin, 'instrument_class', propagate=True)
def receive_instrument_class(mapper, class_):
    """listen for the 'instrument_class' event"""
    event.listen(class_._connect().session,
                 'before_commit', receive_before_commit)
    event.listen(class_._connect().session,
                 'after_rollback', receive_after_rollback)


def receive_after_rollback(session):
    """listen for the 'rollback' event"""
    session._entities_to_sg_sync = set()


def receive_before_commit(session):
    """listen for the 'before commit' event"""
    if not hasattr(session, "_entities_to_sg_sync"):
        return
    entities = session._entities_to_sg_sync
    session._entities_to_sg_sync = set()
    __sync_up(entities)


def entity_sorter(a, b):
    '''Sort entities based on dependencies to eachother'''
    _order = ['User', 'Project', 'Sequence', 'Shot', 'Asset',
              'Task', 'UserTask', 'Take']

    if a.cls_name not in _order:
        return 1
    elif b.cls_name not in _order:
        return -1
    elif _order.index(a.cls_name) > _order.index(b.cls_name):
        return 1
    elif _order.index(a.cls_name) == _order.index(b.cls_name):
        return 0
    else:
        return -1


def __sync_up(entities):
    '''sync local entity changes up to shotgun.'''
    from star.shotgun.sync.core import sync_to_shotgun, _LOCAL

    # Sync is already in progress?
    if _LOCAL.SYNC_LOCK:
        return

    counter = 0
    batch_num = 500

    # Sync one by one, based on dependency order.
    for entity in sorted(entities, cmp=entity_sorter):
        try:
            sync_to_shotgun(entity)
            LOG.debug(
                "before-commit sync: {} -> {}".format(entity, entity.shotgun_id))
            counter += 1
            if counter % batch_num == 0:
                time.sleep(2)
                counter = 0
        except Exception:
            LOG.error(traceback.format_exc())
            # raise
