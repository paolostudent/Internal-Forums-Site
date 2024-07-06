import os
from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from .models import Forum, Post, Comment
from . import db
from flask_wtf import FlaskForm
from wtforms import TextAreaField, HiddenField, SubmitField, FileField, StringField
from wtforms.validators import DataRequired
from flask_wtf.file import FileAllowed
from flask import current_app

# Configuration for the uploads folder and allowed extensions
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Ensure the upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Blueprint for forums
forums = Blueprint('forums', __name__)

# Function to check if a filename has an allowed extension
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Form for creating and updating posts
class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    media = FileField('Upload Media', validators=[FileAllowed(ALLOWED_EXTENSIONS)])
    submit = SubmitField('Post')

# Form for comments
class CommentForm(FlaskForm):
    content = TextAreaField('Content', validators=[DataRequired()])
    parent_id = HiddenField('Parent ID')  # Hidden field for the parent comment
    submit = SubmitField('Post')

# Route for forum home
@forums.route('/forums')
def forum_home():
    forums = Forum.query.all()
    return render_template('forums.html', forums=forums, user=current_user)

# Route for viewing a forum
@forums.route('/forum/<int:forum_id>')
def view_forum(forum_id):
    forum = Forum.query.get_or_404(forum_id)
    posts = Post.query.filter_by(forum_id=forum_id).all()
    return render_template('forum.html', forum=forum, posts=posts, user=current_user)

# Route for creating a new forum
@forums.route('/forum/new', methods=['GET', 'POST'])
@login_required
def create_forum():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')

        if not title:
            flash('Title is required!', category='error')
        else:
            new_forum = Forum(title=title, description=description)
            db.session.add(new_forum)
            db.session.commit()
            flash('Forum created!', category='success')
            return redirect(url_for('forums.forum_home'))

    return render_template('create_forum.html', user=current_user)

# Route for creating a new post with optional media upload
@forums.route('/forum/<int:forum_id>/post/new', methods=['GET', 'POST'])
@login_required
def create_post(forum_id):
    form = PostForm()
    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data
        file = form.media.data
        
        filename = None
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # Use `app` context directly if `current_app` is causing issues
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
        
        new_post = Post(
            title=title,
            content=content,
            media_filename=filename,
            user_id=current_user.id,
            forum_id=forum_id
        )
        db.session.add(new_post)
        db.session.commit()
        flash('Post created!', category='success')
        return redirect(url_for('forums.view_forum', forum_id=forum_id))
    
    return render_template('create_post.html', form=form, user=current_user, forum_id=forum_id)

# Route for viewing a post and its comments
@forums.route('/forum/<int:forum_id>/post/<int:post_id>')
def view_post(forum_id, post_id):
    post = Post.query.get_or_404(post_id)
    comments = Comment.query.filter_by(post_id=post_id, parent_id=None).all()
    form = CommentForm()
    return render_template('view_post.html', post=post, comments=comments, user=current_user, form=form)

# Route for adding a comment to a post
@forums.route('/forum/<int:forum_id>/post/<int:post_id>/comment', methods=['POST'])
@login_required
def add_comment(forum_id, post_id):
    form = CommentForm()
    if form.validate_on_submit():
        content = form.content.data
        new_comment = Comment(content=content, user_id=current_user.id, post_id=post_id)
        db.session.add(new_comment)
        db.session.commit()
        flash('Comment added!', category='success')
    return redirect(url_for('forums.view_post', forum_id=forum_id, post_id=post_id))

# Route for replying to a comment
@forums.route('/forum/<int:forum_id>/post/<int:post_id>/comment/<int:comment_id>/reply', methods=['POST'])
@login_required
def reply_comment(forum_id, post_id, comment_id):
    form = CommentForm()
    if form.validate_on_submit():
        content = form.content.data
        new_reply = Comment(content=content, user_id=current_user.id, post_id=post_id, parent_id=comment_id)
        db.session.add(new_reply)
        db.session.commit()
        flash('Reply added!', category='success')
    return redirect(url_for('forums.view_post', forum_id=forum_id, post_id=post_id))
