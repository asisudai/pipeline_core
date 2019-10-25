import os
import re
import copy
import yaml

# Schemas root folder
SCHEMAS_ROOT = os.path.join(os.path.dirname(__file__), 'schemas')
__SCHEMAS = dict()
_REG = re.compile(r'(\<([\w\.]+)(.*?)\>)')


def iter_schema(schema_name, values, app=None, owner=None):

    raw_schema = read_schema(schema_name)
    raw_schema_copy = copy.deepcopy(raw_schema)
    values = _expand_values(values)

    for item in _iter_schema_items(raw_schema_copy, values, app=app, owner=owner):
        yield item


def _iter_schema_items(raw_schema, values, app=None, owner=None, force=False, _previous_path=''):
    '''
    Iterator through schemas and yield parsed items.
    '''
    current_path = os.path.join(_previous_path, raw_schema.get('name', ''))

    if 'name' in raw_schema:

        yield {'path': _parse_raw_path(current_path, values),
               'umask': raw_schema.get('umask'),
               'pgrp': raw_schema.get('pgrp'),
               'type': "folder"}

        for child in raw_schema.get("children", []):
            for element in _iter_schema_items(child, values, app, owner, force, current_path):
                yield element


def _expand_values(values):
    '''Expend entities to include parents'''
    def _get_parent(entity):
        try:
            parent = entity.parent
            getattr(parent, 'cls_name')
            return parent
        except Exception:
            return

    result = {}
    for key, val in values.items():
        parent = _get_parent(val)
        while parent:
            if parent.cls_name() not in result:
                result[parent.cls_name()] = parent
                parent = _get_parent(parent)

    values.update(result)
    values = {k.lower(): v for k, v in values.items()}
    return values


def _parse_raw_path(raw_path, values):
    for regex in _REG.finditer(raw_path):
        (placeholder, entity_placeholder, func) = regex.groups()

        if '.' in entity_placeholder:
            (entity, attr) = entity_placeholder.split(".")
            entity = entity.lower()
            if entity not in values:
                raise ValueError('Missing entity {!r} for path {!r}'.format(entity, raw_path))
            placeholder_value = getattr(values[entity], attr)
        else:
            placeholder_value = entity_placeholder

        raw_path = raw_path.replace(placeholder, placeholder_value)

    return raw_path


def read_schema(name):
    '''
    Return schema with given name.

        Args:
            name (str) : schema's name.

        Return:
            schema's dict
    '''

    # Pre-read schemas
    if __SCHEMAS.get(name):
        return __SCHEMAS[name]

    filename = 'folders_{}.schema'.format(name)
    path = os.path.join(SCHEMAS_ROOT, filename)

    if not os.path.exists(path):
        raise SchemaNotFound('Schema filename not found:{!r}'.format(path))

    with open(path, mode='r') as fs:
        schema_list = [t for t in yaml.load_all(fs)]
        assert len(schema_list) == 1, 'Schema expected to have one root item only {} {!r}'.format(
            schema_list, path)
        schema_data = schema_list.pop()

    __SCHEMAS[name] = schema_data
    return schema_data


class SchemaNotFound(TypeError):
    pass
