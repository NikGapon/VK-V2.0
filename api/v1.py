
from api.news_api import *


def init(app, auth):
    api = Api(app)
    api.add_resource(NewsListApi, '/api/v1/news', resource_class_args=[auth])
    api.add_resource(NewsApi, '/api/v1/news/<int:id>', resource_class_args=[auth])
