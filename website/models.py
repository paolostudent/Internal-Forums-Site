from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship, backref

# Association table for the many-to-many relationship between User and Forum
user_forum_association = db.Table('user_forum_association',
                                  db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
                                  db.Column('forum_id', db.Integer, db.ForeignKey('forum.id'), primary_key=True)
                                  )

# Model representing a user in the system
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    first_name = db.Column(db.String(150))
    password = db.Column(db.String(150))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    notes = db.relationship('Note', backref='author', lazy=True)
    posts = db.relationship('Post', backref='author', lazy=True)
    comments = db.relationship('Comment', backref='author', lazy=True)
    forums = db.relationship('Forum', secondary=user_forum_association, back_populates='users')
    is_admin = db.Column(db.Boolean, default=False)

# Model representing a note associated with a user
class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(10000))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

# Model representing a forum
class Forum(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    posts = db.relationship('Post', backref='forum', lazy=True, cascade='all, delete-orphan')
    users = db.relationship('User', secondary=user_forum_association, back_populates='forums')

# Model representing a post in a forum
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    media_filename = db.Column(db.String(100), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    forum_id = db.Column(db.Integer, db.ForeignKey('forum.id'), nullable=False)
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    comments = db.relationship('Comment', backref='post', lazy=True, cascade='all, delete-orphan')

# Model representing a comment on a post
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('comment.id'), nullable=True)
    replies = db.relationship('Comment', backref=backref('parent', remote_side=[id]), lazy='dynamic', cascade='all, delete-orphan')
    date = db.Column(db.DateTime(timezone=True), default=func.now())
