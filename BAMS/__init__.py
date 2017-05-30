from pyramid.config import Configurator

from urllib.parse import urlparse

from gridfs import GridFS
from pymongo import MongoClient

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(settings=settings)
    # '''for MongoDB
    # '''
    #
    db_url = urlparse(settings['mongo_uri'])
    config.registry.db = MongoClient(
        host=db_url.hostname,
        port=db_url.port,
    )

    def add_db(request):
        db = config.registry.db[db_url.path[1:]]
        if db_url.username and db_url.password:
            db.authenticate(db_url.username, db_url.password)
        return db

    def add_fs(request):
        return GridFS(request.db)
    #
    config.add_request_method(add_db, 'db', reify=True)
    config.add_request_method(add_fs, 'fs', reify=True)

    config.include('pyramid_chameleon')
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/')
    config.add_route('quotation_new', '/quotation/new')
    config.add_route('summary', '/summary')
    config.add_route('settings', '/settings')
    config.add_route('quotation_create', '/quotation/create')
    config.add_route('quotation_edit', '/quotation/edit/{quotation_no}')
    config.add_route('quotation_json', 'quotation.json')
    config.scan()
    return config.make_wsgi_app()
