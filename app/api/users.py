from flask import current_app, url_for
from flask_restful import Resource, reqparse
from . import restful
from ..models import User, Post


class GetUser(Resource):
    def get(self, id):
        user = User.query.get_or_404(id)
        return user.to_json()


class GetUserPosts(Resource):
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
            prev = url_for('api.get_user_posts', id=id, page=page - 1)
        next = None
        if pagination.has_next:
            next = url_for('api.get_user_posts', id=id, page=page + 1)
        return {
            'posts': [post.to_json() for post in posts],
            'prev': prev,
            'next': next,
            'count': pagination.total
        }


class GetUserFollowedPosts(Resource):
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
            prev = url_for('api.get_user_followed_posts', id=id, page=page - 1)
        next = None
        if pagination.has_next:
            next = url_for('api.get_user_followed_posts', id=id, page=page + 1)
        return {
            'posts': [post.to_json() for post in posts],
            'prev': prev,
            'next': next,
            'count': pagination.total
        }


restful.add_resource(GetUser, '/users/<int:id>', endpoint='get_user')
restful.add_resource(GetUserPosts, '/users/<int:id>/posts/', endpoint='get_user_posts')
restful.add_resource(GetUserFollowedPosts, '/users/<int:id>/timeline/', endpoint='get_user_followed_posts')