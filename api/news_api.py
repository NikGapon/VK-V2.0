from flask_restful import Resource, Api
from flask_restful import reqparse
from flask import jsonify
from flask import abort
import extra.auth as auth
from models import News

news_parser = reqparse.RequestParser()
news_parser.add_argument('title', required=True)
news_parser.add_argument('content', required=True)


class NewsListApi(Resource):
    def __init__(self, auth):
        super(NewsListApi, self).__init__()
        self._auth = auth

    def get(self):
        news = News.query.all()
        return jsonify(news=[i.serialize for i in news])

    def post(self):
        if not self._auth.is_authorized():
            abort(401)
        args = news_parser.parse_args()
        news = News.add(args['title'], args['content'], self._auth.get_user())
        return jsonify(news.serialize)


class NewsApi(Resource):

    def __init__(self, auth):
        super(NewsApi, self).__init__()
        self._auth = auth

    def get(self, id):
        news = News.query.filter_by(id=id).first()
        if not news:
            abort(404)
        return jsonify(news.serialize)

    def delete(self, id):
        if not self._auth.is_authorized():
            abort(401)
        news = News.query.filter_by(id=id).first()
        if news.user_id != self._auth.get_user().id:
            abort(403)
        News.delete(news)
        return jsonify({"deleted": True})
