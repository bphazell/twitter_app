from flask import Blueprint, jsonify, abort, request
from ..models import User, db, Tweet, likes_table
import hashlib
import secrets
import sqlalchemy


def scramble(password: str):
    """Hash and salt the given password"""
    salt = secrets.token_hex(16)
    return hashlib.sha512((password + salt).encode('utf-8')).hexdigest()

bp = Blueprint('users', __name__, url_prefix='/users')

@bp.route('', methods=['GET']) # decorator takes path and list of HTTP verbs

def index():
    users = User.query.all() # ORM performs SELECT query
    result = []
    for u in users:
        result.append(u.serialize()) # build list of Tweets as dictionaries
    return jsonify(result) # return JSON response

@bp.route('/<int:id>', methods=['GET'])
def show(id: int):
    u = User.query.get_or_404(id)
    return jsonify(u.serialize())

@bp.route('', methods=['POST'])
def create():
    if 'username' not in request.json or 'password' not in request.json:
        return abort(400)
    if len(request.json['username']) < 3 or len(request.json['password']) < 8:
        return abort(400)
    u = User(
        username=request.json['username'],
        password=scramble(request.json['password'])
        )
    db.session.add(u)
    db.session.commit()
    return jsonify(u.serialize())

@bp.route('/<int:id>', methods=['DELETE'])
def delete(id:int):
    u = User.query.get_or_404(id)
    try:
        db.session.delete(u) # prepare DELETE statement
        db.session.commit() # execute DELETE statement
        return jsonify(True)
    except:
        # something went wrong :(
        return jsonify(False)

@bp.route('/<int:id>', methods=['PUT', 'PATCH'])
def update(id:int):
    u = User.query.get_or_404(id)
    if "username" not in request.json and "password" not in request.json:
        return abort(404)
    if "username" in request.json:
        if len(request.json["username"]) < 3:
            return abort(404)
        else:
            u.username = request.json["username"]
    if "password" in request.json:
        if len(request.json["password"]) < 8:
            return abort(404)
        else:
            u.password = scramble(request.json["password"])
    try:
        db.session.commit()
        return jsonify(u.serialize())
    except:
        return jsonify(False)
    
@bp.route('/<int:id>/liked_tweets', methods=['GET'])
def liked_tweets(id: int):
    u = User.query.get_or_404(id)
    result = []
    for t in u.liked_tweets:
        result.append(t.serialize())
    return jsonify(result)

# Bonus Task 1

@bp.route('/<int:id>/likes', methods=['Post'])
def likes(id: int):
    if "tweet_id" not in request.json:
        return abort(404)
    tweet_id = request.json["tweet_id"]

    User.query.get_or_404(id)
    Tweet.query.get_or_404(tweet_id)
    
    try:
        stmt = sqlalchemy.insert(likes_table).values(
            user_id=id, tweet_id=tweet_id)
        db.session.execute(stmt)
        db.session.commit()
        return jsonify(True)
    except:
        return jsonify(False)
    
# Bonus Task 2

@bp.route('/<int:user_id>/likes/<int:tweet_id>', methods=['DELETE'])
def unlikes(user_id: int, tweet_id: int):
    User.query.get_or_404(user_id)
    Tweet.query.get_or_404(tweet_id)
    
    try:
        stmt = sqlalchemy.delete(likes_table).where(
            likes_table.c.user_id == user_id,
            likes_table.c.tweet_id == tweet_id
        ) # We delete the tuple (id, tweet_id) from the likes_table
        db.session.execute(stmt)
        db.session.commit()
        return jsonify(True)
    except:
        return jsonify(False)

   

    


        