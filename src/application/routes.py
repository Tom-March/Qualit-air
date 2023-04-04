from flask import Blueprint, render_template

qualitair_app = Blueprint("qualitair", __name__)

# The home route, it brings us to the main page
@qualitair_app.route('/')
def home():
    return render_template("search.html")

# The location route, it brings us to the page of the location
@qualitair_app.route('/location/',methods=["GET", "POST"])
def location():   
    return render_template("location.html")