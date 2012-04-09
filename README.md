This bottle-sqlalchemy plugin integrates SQLAlchemy with your Bottle
application. It injects a SQLAlchemy session in your route and handle the session cycle.

Usage Example:

``` python
import bottle
from bottle import HTTPError
from bottle.ext import sqlalchemy
from sqlalchemy import create_engine, Column, Integer, Sequence, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
engine = create_engine('sqlite:///:memory:', echo=True)

app = bottle.Bottle()
plugin = sqlalchemy.Plugin(
    engine, # SQLAlchemy engine created with create_engine function.
    Base.metadata, # SQLAlchemy metadata, required only if create=True.
    keyword='db', # Keyword used to inject session database in a route (default 'db').
    create=True, # If it is true, execute `metadata.create_all(engine)` when plugin is applied (default False).
    commit=True, # If it is true, plugin commit changes after route is executed (default True).
    use_kwargs=False # If it is true and keyword is not defined, plugin uses **kwargs argument to inject session database (default False).
)

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

@app.get('/spam/:eggs', sqlalchemy=dict(use_kwargs=True))
@bottle.view('some_view')
def route_with_view(eggs, db):
    # do something useful here
```    


It is up to you create engine and metadata, because SQLAlchemy has
a lot of options to do it. The plugin just handle the SQLAlchemy
session.