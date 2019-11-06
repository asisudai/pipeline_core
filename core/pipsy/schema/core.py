import os
import re
import yaml

# Schemas root folder
SCHEMAS_ROOT = os.path.join(os.path.dirname(__file__), 'schemas')

REG_KEY   = re.compile(r'(\$[\w]+)')              # $key
REG_SPLIT = re.compile(r'<([\w]+)\.?([\w.]+)?>')  # <entity.attr>

__SCHEMAS_DATA = dict()
__SCHEMAS_PATH = dict()


def get_path(key, fields, schema):
    '''
    Return resolved path using given fields

        Args:
            key     (str) : key to resolve.
            fields (dict) : fields dict.
            schema  (str) : schema's name.

        Retrun:
            resolve path

        Example:
            >>> get_path('shot_root', {'shot':Shot()}, 'film')
            "/projects/unittest/sequence/101/001"
    '''
    raw_path = get_raw_path(key, schema)
    fields = _expand_fields(fields)
    return _resolve_path(raw_path, fields)


def get_raw_path(key, schema):
    '''
    Return a raw path for given key.

        Args:
            key    (str) : key to resolve.
            schema (str) : schema's name.

        Retrun:
            raw path string

        Example:
            >>> get_raw_path('asset_pub', 'film')
            "<project.root>/assets/<asset.type>/<asset.basename>/pub"
    '''
    raw_schema = read_schema(schema)

    if key.lower() not in raw_schema:
        raise KeyError('Key "{}" was not found in "{}".'.format(
            key, __SCHEMAS_PATH[schema]))

    return _get_raw_path_schema(key.lower(), raw_schema)


def get_raw_path_fields(key, schema):
    '''
    Return fields needed to resolve key

        Args:
            key    (str) : key to resolve.
            schema (str) : schema's name.

        Retrun:
            list of fields

        Example:
            >>> get_raw_path_fields('shot_root', 'film')
            ['project', 'sequence', 'shot']

    '''
    raw_path = get_raw_path(key, schema)
    return _get_raw_path_fields(raw_path)


def read_schema(schema):
    '''
    Return schema with given name.

        Args:
            schema (str) : schema's name.

        Return:
            schema's dict
    '''
    if __SCHEMAS_DATA.get(schema):
        return __SCHEMAS_DATA[schema]

    filename = '{}.schema'.format(schema)
    path = os.path.join(SCHEMAS_ROOT, filename)

    if not os.path.exists(path):
        raise SchemaNotFound('Schema filename not found:{!r}'.format(path))

    with open(path, mode='r') as fs:
        schema_list = [t for t in yaml.load_all(fs)]
        assert len(schema_list) == 1, 'Schema expected to have one root item only {} {!r}'.format(
            schema_list, path)
        schema_data = schema_list.pop()

    __SCHEMAS_DATA[schema] = schema_data
    __SCHEMAS_PATH[schema] = path

    return schema_data


def _resolve_path(raw_path, fields):
    '''
    Return a resolved path_schema.
    Will error out schema required missing values.

        Args:
            raw_path  (str) : raw path to resolve.
            fields   (dict) : fields dict.

        Return:
            resovled path
    '''
    needed = _get_raw_path_fields(raw_path)
    missing = list(set(needed).difference(fields))

    if missing:
        raise SchemaMissingFields('Missing fields {} to resolve {!r}'.format(missing, raw_path))

    for reg_element in REG_SPLIT.finditer(raw_path):
        (value, attr) = reg_element.groups()
        value = fields[value]

        if attr and hasattr(value, attr.split(".")[0]):
            value = eval("value.{}".format(attr))

        raw_path = re.sub(reg_element.group(), str(value), raw_path)

    return raw_path


def _get_raw_path_fields(raw_path):
    '''
    Return a list of fields needed to resolve given raw path.
    '''
    result = list()
    for regex in REG_SPLIT.finditer(raw_path):
        field = regex.groups()[0]
        if field not in result:
            result.append(field)
    return result


def _get_raw_path_schema(key, raw_scehma):
    '''Return a raw path_schema string'''
    path_schema  = raw_scehma[key]
    reg_placholder = REG_KEY.search(path_schema)
    while reg_placholder:
        place_value    = reg_placholder.group()
        path_schema  = REG_KEY.sub(raw_scehma[place_value[1:]], path_schema)
        reg_placholder = REG_KEY.search(path_schema)

    return path_schema


def _expand_fields(fields):
    '''
    Expend entity fields to include parent entities

        Example:
            >>> _expand_fields({'shot':Shot})
            {'project':Project, 'sequence':Sequence, 'shot':Shot}
    '''
    def _get_parent(entity):
        try:
            parent = entity.parent
            return parent
        except Exception:
            return

    assert isinstance(fields, dict), 'fields must be type dict. Given {}'.format(type(fields))

    # Copy expended dict to avoid mutation
    fields = fields.copy()

    result = {}
    for key, val in fields.items():
        parent = _get_parent(val)
        while parent:
            if parent.__class__.__name__ not in result:
                result[parent.__class__.__name__] = parent
                parent = _get_parent(parent)

    fields.update(result)
    fields = {k.lower(): v for k, v in fields.items()}
    return fields


class SchemaNotFound(TypeError):
    pass


class SchemaMissingFields(RuntimeError):
    pass
