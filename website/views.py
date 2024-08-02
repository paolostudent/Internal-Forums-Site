from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from .models import Note
from . import db
import json

# Create a Blueprint for the views
views = Blueprint("views", __name__)

# Route to render the home page
@views.route("/",)
@views.route("/home", methods=['GET', 'POST'])
def home():
    # Render the home.html template with the current user
    return render_template("home.html", user=current_user)
