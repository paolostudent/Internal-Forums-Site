# setup_forums.py
from website import db, create_app
from website.models import Forum

def create_forums():
    # Create an application context
    app = create_app()
    with app.app_context():
        forum_titles = ['English', 'Religious Education', 'Mathematics Calculus', 'Mathematics Statistics', 'Physics', 'Chemistry', 'Biology', 'Digital Technologies', 'Technology Hard Materials', 'Food Technology', 'History', 'Geography', 'Commerce',]


        for title in forum_titles:
            if not Forum.query.filter_by(title=title).first():
                forum = Forum(title=title, description=f"{title}")
                db.session.add(forum)
        db.session.commit()

if __name__ == "__main__":
    create_forums()