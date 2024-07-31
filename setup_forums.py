# setup_forums.py
from website import db, create_app
from website.models import Forum

def create_forums():
    # Create an application context
    app = create_app()
    with app.app_context():
        forum_titles = ['English', 'Mathematics', 'Physics', 'Religious Education', 'Physical Education', 'Art - Design', 'Art - Photography', 'Art - Visual Art (Painting/Sculpture)', 'Travel and Tourism', 'World of Work', 'Design and Visual Communication', 'Biology', 'Chemistry', 'Commerce', 'Drama', 'Digital Technologies', 'Geography', 'History', 'Japanese', 'Media Studies', 'Music', 'Materials and Processing Technology - Hard Materials', 'Materials and Processing Technology - Food', 'Materials and Processing Technology - Textiles', 'Manukau Institute of Technology (Trades Academy)'
]
        for title in forum_titles:
            if not Forum.query.filter_by(title=title).first():
                forum = Forum(title=title, description=f"{title}")
                db.session.add(forum)
        db.session.commit()

if __name__ == "__main__":
    create_forums()