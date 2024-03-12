#!/usr/bin/env python3

from flask import Flask, make_response, jsonify, request, session
from flask_migrate import Migrate
from flask_restful import Api, Resource

from models import db, Article, User

app = Flask(__name__)
app.secret_key = b'Y\xf1Xz\x00\xad|eQ\x80t \xca\x1a\x10K'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)

class ClearSession(Resource):

    def delete(self):
    
        session['page_views'] = None
        session['user_id'] = None

        return {}, 204

class IndexArticle(Resource):
    
    def get(self):
        articles = [article.to_dict() for article in Article.query.all()] # No need to jsonify lists
        return articles, 200

class ShowArticle(Resource):

    def get(self, id):
        session['page_views'] = 0 if not session.get('page_views') else session.get('page_views')
        session['page_views'] += 1

        if session['page_views'] <= 3:

            article = Article.query.filter(Article.id == id).first()
            article_json = jsonify(article.to_dict()) # When returning a single item, always jsonify. 

            return make_response(article_json, 200)

        return {'message': 'Maximum pageview limit reached'}, 401

api.add_resource(ClearSession, '/clear')
api.add_resource(IndexArticle, '/articles')
api.add_resource(ShowArticle, '/articles/<int:id>')

class Login(Resource):
    def post(self):
        username = request.get_json()['username'] #request.get_json() returns a dict {'username': 'ana'} with the username value that the user entered 
        # breakpoint() run the frontend with endpoint /login to get the debugging session
        user = User.query.filter(User.username == username).first()
        session['user_id'] = user.id
        return user.to_dict(), 200 # This is also returning json. Json, like dicts, are objects to JS
    
class Logout(Resource):
    def delete(self):
        session['user_id'] = None
        return {}, 204 #No Content status code 
    
class CheckSession(Resource):
    def get(self):
        user_id = session.get('user_id') #session is an object, use the dict method .get() to retrieve values
        if user_id:
            return User.query.filter(User.id == user_id).first().to_dict(), 200
        return {}, 401 # Unauthorized status code
    
api.add_resource(Login, '/login')
api.add_resource(Logout, '/logout')
api.add_resource(CheckSession, '/check_session')

if __name__ == '__main__':
    app.run(port=5555, debug=True)
