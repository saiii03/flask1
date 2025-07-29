from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField,BooleanField, SubmitField
from wtforms.validators import DataRequired,ValidationError,Email,EqualTo
import sqlalchemy as sa
from app import db
from app.models import User
from wtforms import TextAreaField
from wtforms.validators import length

class LoginForm(FlaskForm):
    username=StringField('username',validators=[DataRequired()])
    password=PasswordField('password',validators=[DataRequired()])
    remember_me=BooleanField('Remember me')
    submit=SubmitField("sign in")

class RegistrationForm(FlaskForm):
    username=StringField('username',validators=[DataRequired()])
    email=StringField('Email',validators=[DataRequired(), Email()])
    password1=PasswordField('password',validators=[DataRequired()])
    password2=PasswordField("Repeat password",validators=[DataRequired(),EqualTo('password1')])
    submit=SubmitField('Register')
    
    def validate_username(self , username):
        user=db.session.scalar(sa.select(User).where (User.username == username.data))
        if user is not None:
            raise ValidationError("pick another username")
    
    def validate_email(self , email):
        user=db.session.scalar(sa.select(User).where(User.email==email.data))
        if user is not None:
            raise ValidationError("use different email")


class Editprofileform(FlaskForm):
    username=StringField('username',validators=[DataRequired()])
    about_me=TextAreaField('about_me',validators=[length (min=0,max=140)])
    submit=SubmitField('submit')