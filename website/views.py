from flask import Blueprint     

views = Blueprint('views', __name__)

@views.route('/')
def home():
    return "<h1>Header</h1><p>This is a paragraph</p>"