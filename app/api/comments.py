from flask import g, url_for, current_app
from flask_restful import Resource, reqparse
from .. import db
from ..models import Post, Permission, Comment
from . import restful
from .decorators import permission_required


class CommentsView(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('page', default=1, type=int, location='args')
        super().__init__()

    def get(self):
        page = self.parser.parse_args().get('page')
        pagination = Comment.query.order_by(Comment.timestamp.desc()).paginate(
            page, per_page=current_app.config['FLASKY_COMMENTS_PER_PAGE'],
            error_out=False)
        comments = pagination.items
        prev = None
        if pagination.has_prev:
            prev = url_for('api.comments_view', page=page - 1)
        next = None
        if pagination.has_next:
            next = url_for('api.comments_view', page=page + 1)
        return {
            'comments': [comment.to_json() for comment in comments],
            'prev': prev,
            'next': next,
            'count': pagination.total
        }


class CommentView(Resource):
    def get(self, id):
        comment = Comment.query.get_or_404(id)
        return comment.to_json()


class PostCommentsView(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('page', default=1, type=int, location='args')
        self.parser.add_argument('body', type=str, location='json')
        super().__init__()

    def get(self, id):
        post = Post.query.get_or_404(id)
        page = self.parser.parse_args().get('page')
        pagination = post.comments.order_by(Comment.timestamp.asc()).paginate(
            page, per_page=current_app.config['FLASKY_COMMENTS_PER_PAGE'],
            error_out=False)
        comments = pagination.items
        prev = None
        if pagination.has_prev:
            prev = url_for('api.post_comments_view', id=id, page=page - 1)
        next = None
        if pagination.has_next:
            next = url_for('api.post_comments_view', id=id, page=page + 1)
        return {
            'comments': [comment.to_json() for comment in comments],
            'prev': prev,
            'next': next,
            'count': pagination.total
        }

    @permission_required(Permission.COMMENT)
    def post(self, id):
        args = self.parser.parse_args()
        post = Post.query.get_or_404(id)
        comment = Comment.from_json(args)
        comment.author = g.current_user
        comment.post = post
        db.session.add(comment)
        db.session.commit()
        return comment.to_json(), 201, \
               {'Location': url_for('api.comment_view', id=comment.id)}


restful.add_resource(CommentsView, '/comments/', endpoint='comments_view')
restful.add_resource(CommentView, '/comments/<int:id>', endpoint='comment_view')
restful.add_resource(PostCommentsView, '/posts/<int:id>/comments/', endpoint='post_comments_view')