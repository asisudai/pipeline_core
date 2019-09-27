from pipsy import db


def test_connect_pipeline(capsys):
    '''Connect to pipeline's database'''
    session = db.connect_pipeline()
    databases = session.bind.execute('show databases;').fetchall()
    assert ((db.DATABASE,) in databases), 'expected {} to be in databases'.format(db.DATABASE)
