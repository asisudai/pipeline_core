from pipsy import db
from pipsy.config import config


class TestDB():

    def test_connect_pipeline(self, capsys):
        '''Connect to pipeline's database'''
        connect = db.connect_pipeline()
        databases = connect.engine.execute('show databases;').fetchall()
        assert ((db.DATABASE,) in databases), 'expected {} to be in databases'.format(db.DATABASE)



        
