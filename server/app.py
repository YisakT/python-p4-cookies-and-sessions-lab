from flask import Flask, make_response, jsonify, session
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy_serializer import SerializerMixin

app = Flask(__name__)
app.secret_key = b'Y\xf1Xz\x00\xad|eQ\x80t \xca\x1a\x10K'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

metadata = MetaData(naming_convention={
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
})

db = SQLAlchemy(metadata=metadata)

class Article(db.Model, SerializerMixin):
    __tablename__ = 'articles'

    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String)
    title = db.Column(db.String)
    content = db.Column(db.String)
    preview = db.Column(db.String)
    minutes_to_read = db.Column(db.Integer)
    date = db.Column(db.DateTime, server_default=db.func.now())

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __repr__(self):
        return f'Article {self.id} by {self.author}'

class User(db.Model, SerializerMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)

    articles = db.relationship('Article', backref='user')

    def __repr__(self):
        return f'User {self.name}, ID {self.id}'

migrate = Migrate(app, db)
db.init_app(app)

@app.route('/clear')
def clear_session():
    session['page_views'] = 0
    return {'message': '200: Successfully cleared session data.'}, 200

@app.route('/articles/<int:id>')
def show_article(id):
    # If it's the user's first request, set page views to 0
    session['page_views'] = session.get('page_views', 0) + 1

    # If the user has viewed more than 3 pages
    if session['page_views'] > 3:
        return jsonify({'message': 'Maximum pageview limit reached'}), 401

    s = db.session
    article = s.get(Article, id)

    if not article:
        return jsonify({'message': 'Article not found'}), 404

    return jsonify(article.to_dict())

if __name__ == '__main__':
    app.run(port=5555)
