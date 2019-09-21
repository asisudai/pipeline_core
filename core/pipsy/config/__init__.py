import os
import ConfigParser

CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'config.ini')
config = ConfigParser.ConfigParser()
config.read(CONFIG_FILE)
