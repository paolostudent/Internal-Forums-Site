from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app, abort
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from .models import Forum, Post, Comment
from . import db
from flask_wtf import FlaskForm
from wtforms import TextAreaField, HiddenField, SubmitField, FileField, StringField
from wtforms.validators import DataRequired
from flask_wtf.file import FileAllowed
import os

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

forums = Blueprint('forums', __name__)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    media = FileField('Upload Media', validators=[FileAllowed(ALLOWED_EXTENSIONS)])
    submit = SubmitField('Post')

class CommentForm(FlaskForm):
    content = TextAreaField('Content', validators=[DataRequired()])
    parent_id = HiddenField('Parent ID')
    submit = SubmitField('Post')

@forums.route('/forums')
def forum_home():
    forums = Forum.query.all()
    return render_template('forums.html', forums=forums, user=current_user)

@forums.route('/forums/<string:forum_title>')
@login_required
def view_forum(forum_title):
    forum = Forum.query.filter_by(title=forum_title).first_or_404()
    if forum not in current_user.forums:
        flash("You are not subscribed to this forum.", "error")
        return redirect(url_for('forums.forum_home'))
    posts = Post.query.filter_by(forum_id=forum.id).all()
    return render_template('forum.html', forum=forum, posts=posts, user=current_user)

@forums.route('/forums/<string:forum_title>/post/new', methods=['GET', 'POST'])
@login_required
def create_post(forum_title):
    form = PostForm()
    forum = Forum.query.filter_by(title=forum_title).first_or_404()
    if forum not in current_user.forums:
        flash("You are not subscribed to this forum.", "error")
        return redirect(url_for('forums.forum_home'))

    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data
        file = form.media.data
        
        filename = None
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
        
        new_post = Post(
            title=title,
            content=content,
            media_filename=filename,
            user_id=current_user.id,
            forum_id=forum.id
        )
        db.session.add(new_post)
        db.session.commit()
        flash('Post created!', category='success')
        return redirect(url_for('forums.view_forum', forum_title=forum.title))
    
    return render_template('create_post.html', form=form, user=current_user, forum=forum)

@forums.route('/forums/<string:forum_title>/post/<int:post_id>')
@login_required
def view_post(forum_title, post_id):
    forum = Forum.query.filter_by(title=forum_title).first_or_404()
    if forum not in current_user.forums:
        flash("You are not subscribed to this forum.", "error")
        return redirect(url_for('forums.forum_home'))
    
    post = Post.query.get_or_404(post_id)
    comments = Comment.query.filter_by(post_id=post_id, parent_id=None).all()
    form = CommentForm()
    return render_template('view_post.html', post=post, comments=comments, user=current_user, form=form)

@forums.route('/forums/<string:forum_title>/post/<int:post_id>/comment', methods=['POST'])
@login_required
def add_comment(forum_title, post_id):
    forum = Forum.query.filter_by(title=forum_title).first_or_404()
    if forum not in current_user.forums:
        flash("You are not subscribed to this forum.", "error")
        return redirect(url_for('forums.forum_home'))

    form = CommentForm()
    if form.validate_on_submit():
        content = form.content.data
        new_comment = Comment(content=content, user_id=current_user.id, post_id=post_id)
        db.session.add(new_comment)
        db.session.commit()
        flash('Comment added!', category='success')
    return redirect(url_for('forums.view_post', forum_title=forum_title, post_id=post_id))

@forums.route('/forums/<string:forum_title>/post/<int:post_id>/comment/<int:comment_id>/reply', methods=['POST'])
@login_required
def reply_comment(forum_title, post_id, comment_id):
    forum = Forum.query.filter_by(title=forum_title).first_or_404()
    if forum not in current_user.forums:
        flash("You are not subscribed to this forum.", "error")
        return redirect(url_for('forums.forum_home'))

    form = CommentForm()
    if form.validate_on_submit():
        content = form.content.data
        new_reply = Comment(content=content, user_id=current_user.id, post_id=post_id, parent_id=comment_id)
        db.session.add(new_reply)
        db.session.commit()
        flash('Reply added!', category='success')
    return redirect(url_for('forums.view_post', forum_title=forum_title, post_id=post_id))
