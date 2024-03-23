from hashlib import md5

from flask import Flask, render_template, request, jsonify
import requests
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Text, ForeignKey
from flask_sqlalchemy import SQLAlchemy
from forms import AddCafe
from flask_bootstrap import Bootstrap5
from gravatar import gravatar_url
from cafe_api import CafeApi

# User Preferences
endpoint = "http://127.0.0.1:5123"
featured_cafe = "Old Spike"

app = Flask(__name__)
app.config['SECRET_KEY'] = 'S4er8xDtpLa5YzB8BmgnbctSIuhtUEl31yUrIBkjJYxSkGLLmvjYVdc6zj3Q7NB'
Bootstrap5(app)
app.jinja_env.globals.update(gravatar_url=gravatar_url)

# initialize cafe api handler class
cafe_api = CafeApi(endpoint)


# TODO: Create user login

# # configure flask login manager
# login_manager = LoginManager()
# login_manager.init_app(app)


# @login_manager.user_loader
# def load_user(user_id):
#     return db.get_or_404(User, user_id)


# # CREATE DATABASE
# class Base(DeclarativeBase):
#     pass


# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
# db = SQLAlchemy(model_class=Base)
# db.init_app(app)


# class User(UserMixin, db.Model):
#     __tablename__ = "users"
#     id: Mapped[int] = mapped_column(Integer, primary_key=True)
#     email: Mapped[str] = mapped_column(String(100), unique=True)
#     password: Mapped[str] = mapped_column(String(100))
#     name: Mapped[str] = mapped_column(String(100))


# def get_random_cafe():
#     """
#     Return a random cafe
#     :return: Cafe as dictionary
#     """
#     endpoint_url = endpoint + "/random"
#     response = requests.get(url=endpoint_url)
#     response.raise_for_status()
#     return response.json()['cafe']
#
#
# def get_cafe_by_name(name):
#     """
#     Gets a cafe by name
#     :return: cafe as dictionary
#     """
#     endpoint_url = endpoint + "/get_by_name?name=" + name
#     response = requests.get(url=endpoint_url)
#     response.raise_for_status()
#     return response.json()['cafe']


@app.route("/")
def home():
    # Set page titles and headings
    page_title = "Cafe Finder"
    heading = "Discover your happy place"
    sub_heading = "Find the perfect cafe for you to work, relax, or just enjoy the brew."

    # get cafes from database
    rand_cafe = cafe_api.get_random_cafe()
    featured = cafe_api.get_cafe_by_name(featured_cafe)

    # get new cafe if it matches the featured cafe
    while rand_cafe['id'] == featured['id']:
        rand_cafe = cafe_api.get_random_cafe()

    # add title to each cafe
    featured['title'] = "Featured Cafe"
    rand_cafe['title'] = "Random Cafe"

    # combine cafes into a list to send the web page for display
    cafes = [featured, rand_cafe]

    return render_template("index.html", page_title=page_title, f_cafe=featured, r_cafe=rand_cafe,
                           heading=heading, sub_heading=sub_heading, cafes=cafes)


@app.route("/search")
def search():
    page_title = "Search"
    return render_template("search.html", page_title=page_title)


@app.route("/add", methods=["POST", "GET"])
def add():
    # WT form
    form = AddCafe()

    # Set page titles and headings
    page_title = "Add"
    heading = "Add a Cafe"
    sub_heading = "Share a great cafe with us."

    if form.validate_on_submit():
        parameters = cafe_api.add_cafe(
            name=request.form.get('name'),
            location=request.form.get('location'),
            img_url=request.form.get('img_url'),
            map_url=request.form.get('map_url'),
            coffee_price=request.form.get('coffee_price'),
            has_wifi=request.form.get('has_wifi'),
            has_sockets=request.form.get('has_outlets'),
            has_toilet=request.form.get('has_toilet'),
            can_take_calls=request.form.get('can_take_calls'),
            seats=request.form.get('seats'),
        )

        cafe = parameters
        cafe['title'] = "New Cafe Added"
        return render_template("add_success.html", cafe=cafe, page_title=page_title)

    return render_template("add.html", form=form, page_title=page_title, heading=heading, sub_heading=sub_heading)


@app.route("/edit")
def edit():
    # Set page titles and headings
    page_title = "Edit"
    heading = "Add a Cafe"
    sub_heading = "Share a great cafe with us."
    return render_template("edit.html", page_title=page_title, heading=heading, sub_heading=sub_heading)


@app.route("/remove", methods=["GET"])
def remove():
    cafe_id = request.values.get('id')

    # remove the cafe using the API
    r = cafe_api.remove_cafe(cafe_id)

    # Set page titles and headings
    page_title = "Report Closed"
    heading = "Cafe Closed"

    if not r.keys():
        sub_heading = "API Connection error."
    else:
        for key in r.keys():
            for inner_key in r[key].keys():
                print(inner_key)
                sub_heading = r[key][inner_key]
    return render_template("index.html", page_title=page_title, heading=heading, sub_heading=sub_heading)


@app.route('/all')
def show_all():
    # Set page titles and headings
    page_title = "All Cafes"
    heading = "Show all Cafes"
    sub_heading = "We are sure you'll find one you love."

    cafes = cafe_api.get_all()
    return render_template("index.html", page_title=page_title, heading=heading, sub_heading=sub_heading, cafes=cafes)


if __name__ == '__main__':
    app.run(debug=True, port=1234)
