from flask import request, g, url_for, current_app
from flask_restful import Resource, reqparse
from .. import db
from ..models import Post, Permission
from . import restful
from .decorators import permission_required
from .errors import forbidden


class GetPosts(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('page', default=1, type=int, location='args')
        self.parser.add_argument('title', type=str, location='json')
        self.parser.add_argument('body', type=str, location='json')
        super().__init__()

    def get(self):
        page = self.parser.parse_args().get('page')
        pagination = Post.query.order_by(Post.timestamp.desc()).paginate(
            page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
            error_out=False)
        posts = pagination.items
        prev = None
        if pagination.has_prev:
            prev = url_for('api.get_posts', page=page - 1)
        next = None
        if pagination.has_next:
            next = url_for('api.get_posts', page=page + 1)
        return {
            'posts': [post.to_json() for post in posts],
            'prev': prev,
            'next': next,
            'count': pagination.total
        }

    @permission_required(Permission.WRITE)
    def post(self):
        args = self.parser.parse_args()
        post = Post.from_json(args)
        post.author = g.current_user
        db.session.add(post)
        db.session.commit()
        return post.to_json(), 201,\
               {'Location': url_for('api.get_post', id=post.id)}


class GetPost(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('body', type=str, location='json')
        super().__init__()

    def get(self, id):
        post = Post.query.get_or_404(id)
        return post.to_json()

    @permission_required(Permission.WRITE)
    def put(self, id):
        args = self.parser.parse_args()
        post = Post.query.get_or_404(id)
        if g.current_user != post.author and \
                not g.current_user.can(Permission.ADMIN):
            return forbidden('Insufficient permissions')
        post.body = args.get('body', post.body)
        db.session.add(post)
        db.session.commit()
        return post.to_json()


restful.add_resource(GetPosts, '/posts/', endpoint='get_posts')
restful.add_resource(GetPost, '/posts/<int:id>', endpoint='get_post')

