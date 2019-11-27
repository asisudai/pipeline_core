
from .. entities import BaseEntity

# Publish entity currently supports the following parent entities
SUPPORTED_ENTITIES = ['Sequence', 'Shot', 'Instance', 'Asset']

class PublishBase(object):

    def __init__(self, entity):
        '''
        PublishBase - framework for publishing files and folder into the filesystem and database.
        Create a Publish entity.

            Args:
                entity (Entity) : Publish parent Entity.
        '''
        BaseEntity.assert_isinstance(entity, SUPPORTED_ENTITIES)


    def publish(self):
        self.hook_prepublish()
