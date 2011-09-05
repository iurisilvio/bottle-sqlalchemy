#!/usr/bin/python
import bottle
from bottle import route, redirect, put, delete
from bottle.ext.sqlalchemy import SQLAlchemyPlugin

from sqlalchemy import create_engine, Column, Integer, Sequence, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
engine = create_engine('sqlite:///:memory:', echo=True)

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
    name = Column(String(50))
    fullname = Column(String(50))
    password = Column(String(12))

    def __init__(self, name, fullname, password):
        self.name = name
        self.fullname = fullname
        self.password = password

    def __repr__(self):
        return "<User('%s','%s', '%s')>" % (self.name, self.fullname, self.password)


@route('/')
def listing(db):
    users = db.query(User)
    result = "".join(["<li>%s</li>" % user.name for user in users])
    return "<ul>%s</ul>" % result

@put('/:name')
def put_name(name, db):
    user = User(name, fullname=name, password=name)
    db.add(user)

# imports to delete_name function
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
create_session = sessionmaker(bind=engine)

@delete('/:name')
def delete_name(name):
    ''' This function don't use the plugin. '''
    session = create_session()
    try:
        user = session.query(User).filter_by(name=name).first()
        session.delete(user)
        session.commit()
    except SQLAlchemyError, e:
        session.rollback()
        raise bottle.HTTPError(500, "Database Error", e)
    finally:
        session.close()


bottle.install(SQLAlchemyPlugin(engine, Base.metadata, create=True))

if __name__ == '__main__':
    bottle.debug(True)
    bottle.run(reloader=True)
