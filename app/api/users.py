from flask import current_app, url_for, abort
from flask_restful import Resource, reqparse
from . import restful
from ..models import User, Post, db


class UserView(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('email', type=str, location='json')
        self.parser.add_argument('password', type=str, location='json')
        super().__init__()

    def get(self, id):
        user = User.query.get_or_404(id)
        return user.to_json()

    def post(self):
        args = self.parser.parse_args()
        email = args.get('email')
        password = args.get('password')
        if email is None or password is None:
            abort(400)
        if User.query.filter_by(email=email).first() is not None:
            abort(400)
        user = User(email=email, password=password)
        db.session.add(user)
        db.session.commit()
        return user.to_json(), 201,\
               {'Location': url_for('api.user_view', id=user.id)}

    def put(self, id):
        pass




class UserPostsView(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('page', default=1, type=int, location='args')
        super().__init__()

    def get(self, id):
        user = User.query.get_or_404(id)
        page = self.parser.parse_args().get('page')
        pagination = user.posts.order_by(Post.timestamp.desc()).paginate(
            page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
            error_out=False)
        posts = pagination.items
        prev = None
        if pagination.has_prev:
            prev = url_for('api.user_posts_view', id=id, page=page - 1)
        next = None
        if pagination.has_next:
            next = url_for('api.user_posts_view', id=id, page=page + 1)
        return {
            'posts': [post.to_json() for post in posts],
            'prev': prev,
            'next': next,
            'count': pagination.total
        }


class UserFollowedPostsView(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('page', default=1, type=int, location='args')
        super().__init__()

    def get(self, id):
        user = User.query.get_or_404(id)
        page = self.parser.parse_args().get('page')
        pagination = user.followed_posts.order_by(Post.timestamp.desc()).paginate(
            page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
            error_out=False)
        posts = pagination.items
        prev = None
        if pagination.has_prev:
            prev = url_for('api.user_followed_posts_view', id=id, page=page - 1)
        next = None
        if pagination.has_next:
            next = url_for('api.user_followed_posts_view', id=id, page=page + 1)
        return {
            'posts': [post.to_json() for post in posts],
            'prev': prev,
            'next': next,
            'count': pagination.total
        }


restful.add_resource(UserView, '/users', '/users/<int:id>', endpoint='user_view')
restful.add_resource(UserPostsView, '/users/<int:id>/posts/', endpoint='user_posts_view')
restful.add_resource(UserFollowedPostsView, '/users/<int:id>/timeline/', endpoint='user_followed_posts_view')