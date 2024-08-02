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

bad_words = ['2g1c', '2 girls 1 cup', 'acrotomophilia', 'alabama hot pocket', 'alaskan pipeline', 'anal', 'anilingus', 'anus', 'apeshit', 'arsehole', 'ass', 'asshole', 'assmunch', 'auto erotic', 'autoerotic', 'babeland', 'baby batter', 'baby juice', 'ball gag', 'ball gravy', 'ball kicking', 'ball licking', 'ball sack', 'ball sucking', 'bangbros', 'bangbus', 'bareback', 'barely legal', 'barenaked', 'bastard', 'bastardo', 'bastinado', 'bbw', 'bdsm', 'beaner', 'beaners', 'beaver cleaver', 'beaver lips', 'beastiality', 'bestiality', 'big black', 'big breasts', 'big knockers', 'big tits', 'bimbos', 'birdlock', 'bitch', 'bitches', 'black cock', 'blonde action', 'blonde on blonde action', 'blowjob', 'blow job', 'blow your load', 'blue waffle', 'blumpkin', 'bollocks', 'bondage', 'boner', 'boob', 'boobs', 'booty call', 'brown showers', 'brunette action', 'bukkake', 'bulldyke', 'bullet vibe', 'bullshit', 'bung hole', 'bunghole', 'busty', 'butt', 'buttcheeks', 'butthole', 'camel toe', 'camgirl', 'camslut', 'camwhore', 'carpet muncher', 'carpetmuncher', 'chocolate rosebuds', 'cialis', 'circlejerk', 'cleveland steamer', 'clit', 'clitoris', 'clover clamps', 'clusterfuck', 'cock', 'cocks', 'coprolagnia', 'coprophilia', 'cornhole', 'coon', 'coons', 'creampie', 'cum', 'cumming', 'cumshot', 'cumshots', 'cunnilingus', 'cunt', 'darkie', 'date rape', 'daterape', 'deep throat', 'deepthroat', 'dendrophilia', 'dick', 'dildo', 'dingleberry', 'dingleberries', 'dirty pillows', 'dirty sanchez', 'doggie style', 'doggiestyle', 'doggy style', 'doggystyle', 'dog style', 'dolcett', 'domination', 'dominatrix', 'dommes', 'donkey punch', 'double dong', 'double penetration', 'dp action', 'dry hump', 'dvda', 'eat my ass', 'ecchi', 'ejaculation', 'erotic', 'erotism', 'escort', 'eunuch', 'fag', 'faggot', 'fecal', 'felch', 'fellatio', 'feltch', 'female squirting', 'femdom', 'figging', 'fingerbang', 'fingering', 'fisting', 'foot fetish', 'footjob', 'frotting', 'fuck', 'fuck buttons', 'fuckin', 'fucking', 'fucktards', 'fudge packer', 'fudgepacker', 'futanari', 'gangbang', 'gang bang', 'gay sex', 'genitals', 'giant cock', 'girl on', 'girl on top', 'girls gone wild', 'goatcx', 'goatse', 'god damn', 'gokkun', 'golden shower', 'goodpoop', 'goo girl', 'goregasm', 'grope', 'group sex', 'g-spot', 'guro', 'hand job', 'handjob', 'hard core', 'hardcore', 'hentai', 'homoerotic', 'honkey', 'hooker', 'horny', 'hot carl', 'hot chick', 'how to kill', 'how to murder', 'huge fat', 'humping', 'incest', 'intercourse',
             'jack off', 'jail bait', 'jailbait', 'jelly donut', 'jerk off', 'jigaboo', 'jiggaboo', 'jiggerboo', 'jizz', 'juggs', 'kike', 'kinbaku', 'kinkster', 'kinky', 'knobbing', 'leather restraint', 'leather straight jacket', 'lemon party', 'livesex', 'lolita', 'lovemaking', 'make me come', 'male squirting', 'masturbate', 'masturbating', 'masturbation', 'menage a trois', 'milf', 'missionary position', 'mong', 'motherfucker', 'mound of venus', 'mr hands', 'muff diver', 'muffdiving', 'nambla', 'nawashi', 'negro', 'neonazi', 'nigga', 'nigger', 'nig nog', 'nimphomania', 'nipple', 'nipples', 'nsfw', 'nsfw images', 'nude', 'nudity', 'nutten', 'nympho', 'nymphomania', 'octopussy', 'omorashi', 'one cup two girls', 'one guy one jar', 'orgasm', 'orgy', 'paedophile', 'paki', 'panties', 'panty', 'pedobear', 'pedophile', 'pegging', 'penis', 'phone sex', 'piece of shit', 'pikey', 'pissing', 'piss pig', 'pisspig', 'playboy', 'pleasure chest', 'pole smoker', 'ponyplay', 'poof', 'poon', 'poontang', 'punany', 'poop chute', 'poopchute', 'porn', 'porno', 'pornography', 'prince albert piercing', 'pthc', 'pubes', 'pussy', 'queaf', 'queef', 'quim', 'raghead', 'raging boner', 'rape', 'raping', 'rapist', 'rectum', 'reverse cowgirl', 'rimjob', 'rimming', 'rosy palm', 'rosy palm and her 5 sisters', 'rusty trombone', 'sadism', 'santorum', 'scat', 'schlong', 'scissoring', 'semen', 'sex', 'sexcam', 'sexo', 'sexy', 'sexual', 'sexually', 'sexuality', 'shaved beaver', 'shaved pussy', 'shemale', 'shibari', 'shit', 'shitblimp', 'shitty', 'shota', 'shrimping', 'skeet', 'slanteye', 'slut', 's&m', 'smut', 'snatch', 'snowballing', 'sodomize', 'sodomy', 'spastic', 'spic', 'splooge', 'splooge moose', 'spooge', 'spread legs', 'spunk', 'strap on', 'strapon', 'strappado', 'strip club', 'style doggy', 'suck', 'sucks', 'suicide girls', 'sultry women', 'swastika', 'swinger', 'tainted love', 'taste my', 'tea bagging', 'threesome', 'throating', 'thumbzilla', 'tied up', 'tight white', 'tit', 'tits', 'titties', 'titty', 'tongue in a', 'topless', 'tosser', 'towelhead', 'tranny', 'tribadism', 'tub girl', 'tubgirl', 'tushy', 'twat', 'twink', 'twinkie', 'two girls one cup', 'undressing', 'upskirt', 'urethra play', 'urophilia', 'vagina', 'venus mound', 'viagra', 'vibrator', 'violet wand', 'vorarephilia', 'voyeur', 'voyeurweb', 'voyuer', 'vulva', 'wank', 'wetback', 'wet dream', 'white power', 'whore', 'worldsex', 'wrapping men', 'wrinkled starfish', 'xx', 'xxx', 'yaoi', 'yellow showers', 'yiffy', 'zoophilia', '🖕']


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

forums = Blueprint('forums', __name__)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def contains_bad_words(text, bad_words):
    text = text.lower()
    for word in bad_words:
        if word in text:
            return True
    return False


class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    media = FileField('Upload Media', validators=[
                      FileAllowed(ALLOWED_EXTENSIONS)])
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
        return redirect(url_for('views.home'))
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

        if contains_bad_words(title, bad_words) or contains_bad_words(content, bad_words):
            flash('Your post contains inappropriate language. Please remove any bad words and try again.', category='error')
            return render_template('create_post.html', form=form, user=current_user, forum=forum)

        filename = None
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(
                current_app.config['UPLOAD_FOLDER'], filename)
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
    return render_template('view_post.html', post=post, comments=comments, user=current_user, form=form, forum=forum)


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

        if contains_bad_words(content, bad_words):
            flash('Your comment contains inappropriate language. Please remove any bad words and try again.', category='error')
            return redirect(url_for('forums.view_post', forum_title=forum_title, post_id=post_id))

        new_comment = Comment(
            content=content, user_id=current_user.id, post_id=post_id)
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

        if contains_bad_words(content, bad_words):
            flash('Your reply contains inappropriate language. Please remove any bad words and try again.', category='error')
            return redirect(url_for('forums.view_post', forum_title=forum_title, post_id=post_id))

        new_reply = Comment(content=content, user_id=current_user.id,
                            post_id=post_id, parent_id=comment_id)
        db.session.add(new_reply)
        db.session.commit()
        flash('Reply added!', category='success')
    return redirect(url_for('forums.view_post', forum_title=forum_title, post_id=post_id))


@forums.route('/forums/post/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    forum_title = post.forum.title

    # Check if the current user is either the creator of the post or an admin
    if post.user_id != current_user.id and not current_user.is_admin:
        abort(403)  # Forbidden

    db.session.delete(post)
    db.session.commit()
    flash('Post deleted successfully.', 'success')

    return redirect(url_for('forums.view_forum', forum_title=forum_title))


@forums.route('/forums/post/<int:post_id>/comment/<int:comment_id>/delete', methods=['POST'])
@login_required
def delete_comment(post_id, comment_id):
    comment = Comment.query.get_or_404(comment_id)
    forum_title = comment.post.forum.title

    # Check if the current user is either the creator of the comment or an admin
    if comment.user_id != current_user.id and not current_user.is_admin:
        abort(403)  # Forbidden

    db.session.delete(comment)
    db.session.commit()
    flash('Comment deleted successfully.', 'success')

    return redirect(url_for('forums.view_post', forum_title=forum_title, post_id=post_id))


@forums.route('/forums/post/<int:post_id>/comment/<int:comment_id>/reply/<int:reply_id>/delete', methods=['POST'])
@login_required
def delete_reply(post_id, comment_id, reply_id):
    reply = Comment.query.get_or_404(reply_id)
    forum_title = reply.post.forum.title

    # Check if the current user is either the creator of the reply or an admin
    if reply.user_id != current_user.id and not current_user.is_admin:
        abort(403)  # Forbidden

    db.session.delete(reply)
    db.session.commit()
    flash('Reply deleted successfully.', 'success')

    return redirect(url_for('forums.view_post', forum_title=forum_title, post_id=post_id))
