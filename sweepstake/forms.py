from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, IntegerField, SubmitField, DateField, TimeField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError


#TODO: implement a match update form

class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Log In")


class RegisterForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    password2 = PasswordField("Repeat Password", validators=[DataRequired(), EqualTo("password")])
    bio = TextAreaField("Bio")
    submit = SubmitField("Register")


class UpdateInfoForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    bio = TextAreaField("Bio")
    submit = SubmitField("Update")


class CreateMatchForm(FlaskForm):
    team_a = StringField("Team A", validators=[DataRequired()])
    team_b = StringField("Team B", validators=[DataRequired()])
    date = DateField("Date", format="%d/%m/%Y")
    time = TimeField("Time", format="%H:%M")
    venue = StringField("Venue")
    submit = SubmitField("Create")

    def validate_team_b(self, team_b):
        if team_b.data == self.team_a.data:
            raise ValidationError("Team B cannot be the same as Team A")