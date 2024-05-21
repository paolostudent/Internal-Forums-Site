from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from .models import Forum, Post
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
