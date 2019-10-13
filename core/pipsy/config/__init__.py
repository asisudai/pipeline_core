import os

try:
    # Python 2.7
    import ConfigParser as configparser
except ImportError:
    # Python 3.7
    import configparser

CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'config.ini')
config = configparser.ConfigParser()
config.read(CONFIG_FILE)
