from pipsy import db


class TestDB:

    def test_database(self):
        db.connect_pipeline()
