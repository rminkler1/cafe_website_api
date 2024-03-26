import os
from functools import wraps

from flask import Flask, render_template, request, flash, redirect, url_for, abort
from flask_bootstrap import Bootstrap5
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from werkzeug.security import generate_password_hash, check_password_hash

from cafe_api import CafeApi
from forms import *
from gravatar import gravatar_url

# User Preferences
endpoint = "http://127.0.0.1:5123"
featured_cafe = "Sally B's"

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('FLASK_KEY')
Bootstrap5(app)
# make gravatar_url function accessible in templates
app.jinja_env.globals.update(gravatar_url=gravatar_url)

# initialize cafe api handler class
cafe_api = CafeApi(endpoint)

# configure flask login manager
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)


# CREATE DATABASE
class Base(DeclarativeBase):
    pass


app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLITE_DB')
db = SQLAlchemy(model_class=Base)
db.init_app(app)


class User(UserMixin, db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(100), unique=True)
    password: Mapped[str] = mapped_column(String(100))


with app.app_context():
    db.create_all()


def gravatar(user):
    """
    Get Gravatar
    """
    if user.is_anonymous:
        grav = gravatar_url("cafe@example.com")
    else:
        grav = gravatar_url(user.email)
    return grav


# admin only decorator
def admin_only(function):
    @wraps(function)
    def decorated_function(*args, **kwargs):
        if current_user.is_authenticated and current_user.id == 1:
            return function(*args, **kwargs)
        else:
            return abort(403)

    return decorated_function


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

    my_gravatar = gravatar(current_user)
    return render_template("index.html", page_title=page_title, f_cafe=featured, r_cafe=rand_cafe,
                           heading=heading, sub_heading=sub_heading, cafes=cafes, gravatar=my_gravatar)


@app.route("/search")
def search():
    # Set page titles and headings
    page_title = "Search Results"
    heading = "Search Results"
    sub_heading = "Here are some matches."

    name = request.values.get('name')
    loc = request.values.get('loc')

    cafes = cafe_api.search(name, loc)

    my_gravatar = gravatar(current_user)
    return render_template("index.html", page_title=page_title,
                           heading=heading, sub_heading=sub_heading, cafes=cafes, gravatar=my_gravatar)


@app.route("/add", methods=["POST", "GET"])
@login_required
def add():
    # WT forms
    form = AddCafe()

    # Set page titles and headings
    page_title = "Add"
    heading = "Add a Cafe"
    sub_heading = "Share a great cafe with us."

    my_gravatar = gravatar(current_user)

    if form.validate_on_submit():
        parameters = cafe_api.add_cafe(
            name=request.form.get('name'),
            location=request.form.get('location'),
            img_url=request.form.get('img_url'),
            map_url=request.form.get('map_url'),
            coffee_price=request.form.get('coffee_price'),
            has_wifi=request.form.get('has_wifi'),
            has_sockets=request.form.get('has_sockets'),
            has_toilet=request.form.get('has_toilet'),
            can_take_calls=request.form.get('can_take_calls'),
            seats=request.form.get('seats'),
        )

        cafe = parameters
        cafe['title'] = "New Cafe Added"
        return render_template("success.html", cafe=cafe, page_title=page_title, heading=heading,
                               sub_heading=sub_heading, gravatar=my_gravatar)

    return render_template("form.html", form=form, page_title=page_title, heading=heading,
                           sub_heading=sub_heading, gravatar=my_gravatar)


@app.route("/edit", methods=["GET", "POST"])
@login_required
def edit():
    # Set page titles and headings
    page_title = "Edit"
    heading = "Edit a Cafe"
    sub_heading = "Update a Cafe with the latest information."

    my_gravatar = gravatar(current_user)

    cafe_id = request.values.get('id')

    cafe = cafe_api.get_cafe_by_id(cafe_id)

    edit_form = AddCafe(
        name=cafe['name'],
        location=cafe['location'],
        img_url=cafe['img_url'],
        map_url=cafe['map_url'],
        coffee_price=cafe['coffee_price'],
        has_wifi=cafe['has_wifi'],
        has_sockets=cafe['has_sockets'],
        has_toilet=cafe['has_toilet'],
        can_take_calls=cafe['can_take_calls'],
        seats=cafe['seats'],
    )
    if edit_form.validate_on_submit():
        parameters = cafe_api.edit_cafe(
            cafe_id=cafe_id,
            name=request.form.get('name'),
            location=request.form.get('location'),
            img_url=request.form.get('img_url'),
            map_url=request.form.get('map_url'),
            coffee_price=request.form.get('coffee_price'),
            has_wifi=request.form.get('has_wifi'),
            has_sockets=request.form.get('has_sockets'),
            has_toilet=request.form.get('has_toilet'),
            can_take_calls=request.form.get('can_take_calls'),
            seats=request.form.get('seats'),
        )

        parameters['title'] = "Edited Cafe"
        return render_template('success.html', cafe=parameters, gravatar=my_gravatar,
                               page_title=page_title, heading=heading, sub_heading=sub_heading)

    return render_template("form.html", page_title=page_title, heading=heading,
                           sub_heading=sub_heading, form=edit_form, gravatar=my_gravatar)


@app.route("/remove", methods=["GET"])
@admin_only
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
                sub_heading = r[key][inner_key]

    my_gravatar = gravatar(current_user)

    return render_template("index.html", page_title=page_title, heading=heading,
                           sub_heading=sub_heading, gravatar=my_gravatar)


@app.route('/all')
def show_all():
    # Set page titles and headings
    page_title = "All Cafes"
    heading = "Show all Cafes"
    sub_heading = "We are sure you'll find one you love."

    cafes = cafe_api.get_all()
    my_gravatar = gravatar(current_user)

    return render_template("index.html", page_title=page_title, heading=heading,
                           sub_heading=sub_heading, cafes=cafes, gravatar=my_gravatar)


@app.route("/register", methods=["GET", "POST"])
def register():
    registration_form = RegisterForm()

    if registration_form.validate_on_submit():
        # Set page titles and headings
        page_title = "Register Success"
        heading = "You are now registered"
        sub_heading = "Add and edit cafes to share with the community."

        # Hashing and salting the password entered by the user
        hash_and_salted_password = generate_password_hash(
            request.form.get('password1'),
            method='pbkdf2:sha256',
            salt_length=16
        )

        # Storing the hashed password in our database
        new_user = User(
            email=request.form.get('email'),
            name=request.form.get('name'),
            password=hash_and_salted_password,
        )

        db.session.add(new_user)
        db.session.commit()

        login_user(new_user)
        my_gravatar = gravatar(current_user)
        return render_template('register_success.html', page_title=page_title, heading=heading,
                               sub_heading=sub_heading, gravatar=my_gravatar)

    # Set page titles and headings
    page_title = "Register"
    heading = "Register"
    sub_heading = "Register to add or edit cafes."
    my_gravatar = gravatar(current_user)
    return render_template("form.html", page_title=page_title, heading=heading,
                           sub_heading=sub_heading, form=registration_form, gravatar=my_gravatar)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    my_gravatar = gravatar(current_user)

    if form.validate_on_submit():
        email = request.form.get('email')
        password = request.form.get('password')

        user = db.session.execute(db.select(User).where(User.email == email)).scalar()
        if not user:
            flash('Login incorrect.')
            return redirect(url_for('login'))
        elif not check_password_hash(user.password, password):
            flash('Login incorrect.')
            return redirect(url_for('login'))
        else:
            login_user(user)
            return redirect(url_for('home'))

    # Set page titles and headings
    page_title = "Login"
    heading = "Login"
    sub_heading = "Log in to access additional features."

    return render_template("form.html", form=form, page_title=page_title, heading=heading,
                           sub_heading=sub_heading, gravatar=my_gravatar)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True, port=1234)
