'''
This bottle-sqlalchemy plugin integrates SQLAlchemy with your Bottle
application. It connects to a database at the beginning of a request,
passes the database handle to the route callback and closes the connection
afterwards.

It inject an argument to all route callbacks that require a `db` keyword.

Usage Example::

    import bottle
    from bottle import HTTPError
    from bottle.ext import sqlalchemy
    from sqlalchemy import create_engine, Column, Integer, Sequence, String
    from sqlalchemy.ext.declarative import declarative_base

    Base = declarative_base()
    engine = create_engine('sqlite:///:memory:', echo=True)

    app = bottle.Bottle()
    plugin = sqlalchemy.Plugin(engine, Base.metadata)
    app.install(plugin)

    class Entity(Base):
        __tablename__ = 'entity'
        id = Column(Integer, Sequence('id_seq'), primary_key=True)
        name = Column(String(50))

        def __init__(self, name):
            self.name = name

        def __repr__(self):
            return "<Entity('%d', '%s')>" % (self.id, self.name)


    @app.get('/:name')
    def show(name, db):
        entity = db.query(Entity).filter_by(name=name).first()
        if entity:
            return {'id': entity.id, 'name': entity.name}
        return HTTPError(404, 'Entity not found.')

    @app.put('/:name')
    def put_name(name, db):
        entity = Entity(name)
        db.add(entity)
'''

__author__ = "Iuri de Silvio"
__version__ = '0.1'
__license__ = 'MIT'

### CUT HERE (see setup.py)

import bottle
from bottle import HTTPError

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import SQLAlchemyError

class SQLAlchemyPlugin(object):

    name = 'sqlalchemy'

    def __init__(self, engine, metadata=None, keyword='db', create=True, autocommit=True):
        if create and not metadata:
            raise TypeError('Define metadata value to create database.')
        self.engine = engine
        self.metadata = metadata
        self.keyword = keyword
        self.create = create
        self.autocommit = autocommit

    def setup(self, app):
        ''' Make sure that other installed plugins don't affect the same
            keyword argument.'''
        for other in app.plugins:
            if not isinstance(other, SQLAlchemyPlugin): continue
            if other.keyword == self.keyword:
                raise PluginError("Found another sqlalchemy plugin with "\
                                  "conflicting settings (non-unique keyword).")

    def apply(self, callback, context):
        import inspect
        args = inspect.getargspec(context['callback'])[0]
        if self.keyword not in args:
            return callback

        self.sessionmaker = sessionmaker(bind=self.engine)
        if self.create:
            self.metadata.create_all(self.engine)

        def wrapper(*args, **kwargs):
            session = self.sessionmaker()
            kwargs[self.keyword] = session

            try:
                rv = callback(*args, **kwargs)
                if self.autocommit:
                    session.commit()
            except SQLAlchemyError, e:
                session.rollback()
                raise HTTPError(500, "Database Error", e)
            finally:
                session.close()
            return rv

        return wrapper


Plugin = SQLAlchemyPlugin
