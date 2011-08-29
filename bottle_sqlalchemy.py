import bottle
from bottle import HTTPError

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base


class SQLAlchemyPlugin(object):

    name = 'sqlalchemy'

    def __init__(self, engine, metadata=None, keyword='db', create=True, autocommit=True):
        if create and not metadata:
            raise TypeError('To create database, define metadata value.')
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
            except Exception, e:
                session.rollback()
                raise HTTPError(500, "Database Error", e)
            finally:
                session.close()
            return rv

        return wrapper


Plugin = SQLAlchemyPlugin
