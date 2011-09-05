import unittest

from sqlalchemy import create_engine, Column, Integer, Sequence, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.session import Session

import bottle
from bottle.ext import sqlalchemy

Base = declarative_base()

class Entity(Base):
    __tablename__ = 'entity'
    id = Column(Integer, Sequence('id_seq'), primary_key=True)


class SQLAlchemyPluginTest(unittest.TestCase):

    def setUp(self):
        self.engine = create_engine('sqlite:///:memory:')
        self.app = bottle.Bottle(catchall=False)

    def test_without_metadata(self):
        sqlalchemy.Plugin(self.engine, create=False)

    def test_without_metadata_create_table_raises(self):
        self.assertRaises(bottle.PluginError, sqlalchemy.Plugin, self.engine, create=True)

    def test_with_commit(self):
        self.app.install(sqlalchemy.Plugin(self.engine, Base.metadata, create=True))

        @self.app.get('/')
        def test(db):
            entity = Entity()
            db.add(entity)
            self._db = db
        self.app({'PATH_INFO':'/', 'REQUEST_METHOD':'GET'}, lambda x, y: None)
        self.assertEqual(self._db.query(Entity).count(), 1)

    def test_with_keyword(self):
        self.app.install(sqlalchemy.Plugin(self.engine))
        @self.app.get('/')
        def test(db):
            self.assertTrue(isinstance(db, Session))
        self.app({'PATH_INFO':'/', 'REQUEST_METHOD':'GET'}, lambda x, y: None)

    def test_without_keyword(self):
        self.app.install(sqlalchemy.Plugin(self.engine, Base.metadata))
        @self.app.get('/')
        def test():
            pass
        self.app({'PATH_INFO':'/', 'REQUEST_METHOD':'GET'}, lambda x, y: None)

        @self.app.get('/2')
        def test(**kw):
            self.assertFalse('db' in kw)
        self.app({'PATH_INFO':'/2', 'REQUEST_METHOD':'GET'}, lambda x, y: None)

    def test_install_two_times(self):
        plugin1 = sqlalchemy.Plugin(self.engine)
        plugin2 = sqlalchemy.Plugin(self.engine, keyword='db2')
        self.app.install(plugin1)
        self.app.install(plugin2)
        self.assertRaises(bottle.PluginError, self.app.install, plugin1)


if __name__ == '__main__':
    unittest.main()
