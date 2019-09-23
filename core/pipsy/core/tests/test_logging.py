import pytest
from pipsy.core import logging


@pytest.fixture
def log(capsys):
    log = logging.getLogger(__name__, level=logging.DEBUG)
    return log


def test_logging(log, capsys):
    # Disable pytest hiding stdout (while in development)
    # with capsys.disabled():
    log.debug('debug statment')
    log.info('info statment')
    log.warning('warning statment')
    log.error('error statment')
    log.critical('critical statment')


def test_log_file(tmpdir_factory):
    log_file = tmpdir_factory.mktemp('pytest').join('test.log')
    file_log = logging.getLogger('x', level=logging.DEBUG, file=log_file.strpath)
    file_log.info('info statment')
    assert log_file.isfile()
    assert log_file.read()

