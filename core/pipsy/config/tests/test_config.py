from pipsy.config import config


def test_config_database():
    assert config.has_section('database'), 'config missing "database" section'
    for opt in ['rdbms', 'host', 'port', 'database', 'user', 'passwd']:
        assert config.get('database', opt), 'missing {!r} option'.format(opt)


def test_publishkind():
    assert config.has_section('publishkind'), 'config missing "publishkind" section'
    for name, kinddict in config.items('publishkind'):
        assert isinstance(eval('dict{}'.format(kinddict)), dict)
