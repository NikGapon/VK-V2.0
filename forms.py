from flask_wtf import FlaskForm
from flask_wtf.file import FileStorage
from wtforms.fields.html5 import EmailField
from wtforms import StringField, SubmitField, TextAreaField, PasswordField, FileField
from wtforms.validators import DataRequired, Email


class NewsCreateForm(FlaskForm):
    title = StringField('Заголовок новости', validators=[DataRequired()])
    content = TextAreaField('Текст новости', validators=[DataRequired()])

    submit = SubmitField('Добавить')


class SmsCreateForm(FlaskForm):
    recipient = StringField('Кому', validators=[DataRequired()])
    text = SubmitField()




class LoginForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Войти')


class UserCreateForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    email = EmailField('Электронная почта', validators=[Email()])
    about_me = TextAreaField('О себе')
    avatar = FileField()
    submit = SubmitField('Создать')


class EditProfileForm(FlaskForm):
    username = StringField('Логин')
    password = PasswordField('Пароль')
    email = EmailField('Электронная почта', validators=[Email()])
    about_me = TextAreaField('О себе')
    avatar = FileField()
    submit = SubmitField('Поменять')

