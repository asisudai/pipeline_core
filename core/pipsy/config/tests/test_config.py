from pipsy.config import config


class TestConfig:

    def test_config_database(self):

        assert config.has_section('database'), 'missing "database" section'
        for opt in ['server', 'port', 'db', 'user', 'passwd']:
            assert config.get('database', opt), 'missing {!r} option'.format(opt)
