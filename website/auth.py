from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User, Forum
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user
from sqlalchemy.orm import joinedload

auth = Blueprint('auth', __name__)

@auth.route('/some_route')
@login_required
def some_route():
    user = User.query.options(joinedload(User.forums)).filter_by(id=current_user.id).first()
    return render_template('some_template.html', user=user)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Email does not exist.', category='error')

    return render_template("login.html", user=current_user)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    # Fetch all forums except 'English' and 'Religious Education'
    forums = Forum.query.filter(~Forum.title.in_(['English', 'Religious Education'])).all()

    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('firstName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        selected_forum_ids = request.form.getlist('forums')

        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already exists.', category='error')
        elif len(email) < 4:
            flash('Email must be greater than 3 characters.', category='error')
        elif len(first_name) < 2:
            flash('First name must be greater than 1 character.', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        elif len(password1) < 7:
            flash('Password must be at least 7 characters.', category='error')
        elif len(selected_forum_ids) != 4:
            flash('You must select exactly 4 forums.', category='error')
        else:
            # Check if there are any users in the database
            is_admin = User.query.count() == 0

            new_user = User(
                email=email,
                first_name=first_name,
                password=generate_password_hash(password1, method='scrypt:32768:8:1'),
                is_admin=is_admin
            )

            # Assign selected forums
            selected_forums = Forum.query.filter(Forum.id.in_(selected_forum_ids)).all()

            # Query for the 'English' and 'Religious Education' forums and add them
            english_forum = Forum.query.filter_by(title='English').first()
            religious_education_forum = Forum.query.filter_by(title='Religious Education').first()
            if english_forum:
                selected_forums.append(english_forum)
            if religious_education_forum:
                selected_forums.append(religious_education_forum)

            new_user.forums = selected_forums

            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('Account created!', category='success')
            return redirect(url_for('views.home'))

    return render_template("sign_up.html", user=current_user, forums=forums)
