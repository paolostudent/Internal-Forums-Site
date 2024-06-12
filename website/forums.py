from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from .models import Forum, Post, Comment
from . import db

forums = Blueprint('forums', __name__)

@forums.route('/forums')
def forum_home():
    forums = Forum.query.all()
    return render_template('forums.html', forums=forums, user=current_user)

@forums.route('/forum/<int:forum_id>')
def view_forum(forum_id):
    forum = Forum.query.get_or_404(forum_id)
    posts = Post.query.filter_by(forum_id=forum_id).all()
    return render_template('forum.html', forum=forum, posts=posts, user=current_user)

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

@forums.route('/forum/<int:forum_id>/post/new', methods=['GET', 'POST'])
@login_required
def create_post(forum_id):
    if request.method == 'POST':
        title = request.form.get('title')  # Get title from form
        content = request.form.get('content')
        if not title:
            flash('Title is required!', category='error')
        elif not content:
            flash('Content is required!', category='error')
        else:
            new_post = Post(title=title, content=content, user_id=current_user.id, forum_id=forum_id)
            db.session.add(new_post)
            db.session.commit()
            flash('Post created!', category='success')
            return redirect(url_for('forums.view_forum', forum_id=forum_id))
    return render_template('create_post.html', user=current_user, forum_id=forum_id)

@forums.route('/forum/<int:forum_id>/post/<int:post_id>')
def view_post(forum_id, post_id):
    post = Post.query.get_or_404(post_id)
    comments = Comment.query.filter_by(post_id=post_id).all()
    return render_template('view_post.html', post=post, comments=comments, user=current_user)

@forums.route('/forum/<int:forum_id>/post/<int:post_id>/comment', methods=['POST'])
@login_required
def add_comment(forum_id, post_id):
    content = request.form.get('content')
    if not content:
        flash('Comment content is required!', category='error')
    else:
        new_comment = Comment(content=content, user_id=current_user.id, post_id=post_id)
        db.session.add(new_comment)
        db.session.commit()
        flash('Comment added!', category='success')
    return redirect(url_for('forums.view_post', forum_id=forum_id, post_id=post_id))

