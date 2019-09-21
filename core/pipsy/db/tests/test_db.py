from pipsy import db


class TestDB:

    def test_database(self):
        connect = db.connect_pipeline()
        assert connect
