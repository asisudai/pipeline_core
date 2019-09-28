from pipsy.config import config


def test_config_database():
    assert config.has_section('database'), 'missing "database" section'
    for opt in ['rdbms', 'host', 'port', 'database', 'user', 'passwd']:
        assert config.get('database', opt), 'missing {!r} option'.format(opt)
