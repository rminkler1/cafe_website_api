from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField
from wtforms.validators import DataRequired, URL, Email


# WTForm for creating a blog post
class AddCafe(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    location = StringField("Location", validators=[DataRequired()])
    img_url = StringField("Image URL", validators=[DataRequired(), URL()])
    map_url = StringField("Map URL", validators=[DataRequired(), URL()])
    coffee_price = StringField("Coffee Price", validators=[DataRequired()])
    has_wifi = BooleanField("WiFi")
    has_sockets = BooleanField("Outlets")
    has_toilet = BooleanField("Has Toilet")
    can_take_calls = BooleanField("Can Take Calls")
    seats = StringField("Seats", validators=[DataRequired()])
    submit = SubmitField("Submit Cafe")

#
#
# class RegisterForm(FlaskForm):
#     email = StringField("Email", validators=[Email()])
#     name = StringField("Name", validators=[DataRequired()])
#     password = PasswordField("Password", validators=[DataRequired()])
#     submit = SubmitField("Register")
#
#
# class LoginForm(FlaskForm):
#     email = StringField("Email", validators=[Email()])
#     password = PasswordField("Password", validators=[DataRequired()])
#     submit = SubmitField("Log in")
#
#
#
