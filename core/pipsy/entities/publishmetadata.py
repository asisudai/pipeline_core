'''Publish entity class'''

# imports
from sqlalchemy import (Table, Column, Index, Integer, JSON,
                        ForeignKey, UniqueConstraint)
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql.expression import cast
from sqlalchemy import func
from .core import Base
from .publish import Publish


class PublishMetadata(Base):

    __table__ = Table('publishmetadata', Base.metadata,
                      Column('publish_id', Integer, ForeignKey(Publish.id),
                             primary_key=True, autoincrement=False),
                      Column('metadata', JSON),

                      Index('ix_publish', 'publish_id'),

                      UniqueConstraint('publish_id', name="uq_publish"),
                      )

    def __repr__(self):
        return "{cls}(publish_id={id})".format(cls=self.__class__.__name__, id=self.publish_id)

    @classmethod
    def set_metadata(cls, publish, data):
        '''
        Set metadata for given Publish.

            Args:
                publish  (Publish) : Task to assignment.
                data        (dict) : data dict to set.
        '''
        cls.assert_isinstance(publish, 'Publish')
        assert isinstance(data, dict), 'data arg must be dict. Given {}'.format(type(data))

        try:
            pubmeta = cls.find_one(publish=publish)
            if pubmeta.metadata != data:
                with pubmeta.session_context():
                    pubmeta.metadata = data
        except NoResultFound:
            PublishMetadata.create(publish=publish, metadata=data)

    @classmethod
    def find(cls, publish=None, key_value=None, has_key=None):
        '''
        Return PublishMetadata instances by query arguments

            Args:
                publish  (Publish) : PublishMetadata parent Publish instance.
                key_value  (Tuple) : PublishMetadata match {'key' : 'value}.
                has_key      (str) : PublishMetadata has 'key'.

            Returns:
                A list of PublishMetadata instances matching find arguments.
        '''
        query = cls.query()

        if publish:
            cls.assert_isinstance(publish, 'Publish')
            query = query.filter(cls.publish_id == publish.id)

        if key_value:
            assert isinstance(key_value, tuple), ('key_value are must be a tuple. Given {}'
                                                 .format(type(key_value)))
            query = query.filter(PublishMetadata.metadata[key_value[0]] == cast(key_value[1], JSON))

        if has_key:
            query = query.filter(func.json_extract(PublishMetadata.metadata,
                                                   '$."{}"'.format(has_key)) != None)

        return query.all()

    @classmethod
    def create(cls, publish, metadata=None):
        '''
        Create a PublishMetadata instance.

            Args:
                publish (Publish) : parent Publish instance.

            Returns:
                New PublishMetadata Instance.
        '''
        cls.assert_isinstance(publish, 'Publish')

        if metadata:
            assert isinstance(metadata, dict), ('metadata arg must be string. Given {}'
                                                .format(type(metadata)))

        data = dict(publish_id = publish.id,
                    metadata   = metadata)

        return super(PublishMetadata, cls).create(**data)
