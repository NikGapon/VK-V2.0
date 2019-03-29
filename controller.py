from os.path import join, dirname, realpath

from flask_restful import abort
import os
from flask import redirect, request, flash, session, url_for, send_from_directory
from flask import render_template as flask_render_template
from werkzeug.utils import secure_filename
import extra.auth as auth
from api.v1 import init as init_api_v1
from forms import UserCreateForm, NewsCreateForm, EditProfileForm, LoginForm, SmsCreateForm, SmsSee

from models import User, News, Sms

Ter_pol = auth.See_chek()

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


def init_route(app, db):

    app.config['UPLOAD_FOLDER'] = join(dirname(realpath(__file__)), 'static')

    # Переопределение стандартного рендера, добавляет параметр auth_user
    def render_template(*args, **kwargs):
        kwargs['auth_user'] = auth.get_user()
        return flask_render_template(*args, **kwargs)

    init_api_v1(app, auth)  # Инициализация маршрутов для API

    @app.route('/')
    @app.route('/index')
    def index():
        db.create_all()
        news_list = News.query

        if not auth.is_authorized():
            return render_template(
                'index.html',
                title='Главная',
                news_list=news_list,

            )

        return render_template(
            'news-list.html',
            title="Главная",
            news_list=news_list
        )

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        try:
            form = LoginForm()
            has_error = False
            login = ''
            if request.method == 'POST':
                username = form.username.data

                if auth.login(username, request.form['password']):
                    return redirect('/')
                else:
                    has_error = True
            return render_template(
                'login.html',
                title='Вход',
                login=login,
                has_error=has_error
            )
        except:
            return redirect('/nousers')

    @app.route('/logout', methods=['GET'])
    def logout():
        auth.logout()
        return redirect('/')

    @app.route('/nousers')
    def db_empty():
        return render_template(
            'dbempty.html',
            title='Пользователей нет')

    @app.route('/user/create', methods=['GET', 'POST'])
    def registration():
        has_error = False
        has_email_error = False
        form = UserCreateForm()
        if form.validate_on_submit():
            username = form.username.data
            email = form.email.data
            password = form.password.data
            about_me = form.about_me.data
            avatar = form.avatar.data
            user = User.query.filter_by(username=username).first()
            if user:
                has_error = True
            else:
                if avatar != '':
                    filename = secure_filename(avatar.filename)
                    avatar.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    User.add(username=username, password=password, email=email, about_me=about_me,
                             avatar='/' + filename)
                else:
                    User.add(username=username, password=password, email=email, about_me=about_me,
                             avatar=url_for('static', filename='default.png'))
                auth.login(username, password)
                return redirect('/')
        return render_template(
            'registration.html',
            title='Зарегистрироваться',
            form=form,
            has_error=has_error,
            has_email_error=has_email_error
        )

    @app.route('/profile', methods=['GET'])
    def profile():
        if not auth.is_authorized():
            return redirect('/login')
        my_news_list = News.query.filter_by(user_id=auth.get_user().id)

        return render_template(
            'my_profile.html',
            title="Мой профиль",
            news_list=my_news_list
        )

    @app.route('/news', methods=['GET'])
    def news_list():

        news_list = News.query
        return render_template(
            'news-list.html',
            title="Новости",
            news_list=news_list
        )

    @app.route('/sms_error')
    def sms_error():
        return render_template('sms_error.html', title='SMS')



    @app.route('/sms-new', methods=['GET', 'POST'])
    def sms_new():

        form = SmsCreateForm()
        if form.validate_on_submit():
            recipient = form.recipient.data
            text = form.text.data
            
            Sms.add(recipient=recipient,  user=auth.get_user(), text=text)

            return redirect('/sms')
        return render_template(
            'sms-new.html',
            title='Отправка сообщений',
            form=form,
        )

        # return render_template('sms-new.html', title='SMS')

    @app.route('/news/create', methods=['GET', 'POST'])
    def news_create_form():
        if not auth.is_authorized():
            return redirect('/login')
        form = NewsCreateForm()
        if form.validate_on_submit():
            title = form.title.data
            content = form.content.data
            News.add(title=title, content=content, user=auth.get_user())
            return redirect('/')
        return render_template(
            'news-create.html',
            title='Создать новость',
            form=form
        )

    @app.route('/news/<int:id>')
    def news_view(id: int):
        news = News.query.filter_by(id=id).first()
        if not news:
            abort(404)
        user = news.user
        return render_template(
            'news-view.html',
            title='Новость - ' + news.title,
            news=news,
            user=user
        )

    @app.route('/news/delete/<int:id>')
    def news_delete(id: int):
        if not auth.is_authorized():
            return redirect('/login')
        news = News.query.filter_by(id=id).first()
        if news.user_id != auth.get_user().id:
            abort(403)
        News.delete(news)
        return redirect('/news')

    @app.route('/success')
    def success():
        return render_template(
                'success.html',
                title='Успех!')

    @app.route('/edit_profile', methods=['GET', 'POST'])
    def edit_profile():
        form = EditProfileForm()
        has_error = False
        user = auth.get_user()
        if form.validate_on_submit():

            username = form.username.data
            password = form.password.data
            about_me = form.about_me.data
            avatar = form.avatar.data
            if avatar != '':
                filename = secure_filename(avatar.filename)
                avatar.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                user.avatar = '/' + filename
            users = User.query.filter_by(username=username).first()
            if users:
                if username != user.username:
                    has_error = True
            if not has_error:
                user.username = username
                if password != '':
                    user.password = password
                user.about_me = about_me


                db.session.commit()
                return redirect('/success')
        else:
            form.username.data = user.username
            form.email.data = user.email
            form.about_me.data = user.about_me

        return render_template(
            'edit_profile.html',
            title='Редактировать профиль',
            form=form,
            has_error=has_error
        )

    @app.route('/game', methods=['GET'])
    def game():
        return render_template('game.html', title='GAME')

    @app.route('/sms', methods=['GET'])
    def sms():
        recipients = Sms.query.all()
        print(recipients)


        if not auth.is_authorized():
            return redirect('/login')
        #user_r = auth.get_user()
        #all = Sms.execute("SELECT * FROM news WHERE recipient = ?", (str(user_r),))
        #print(all)
        if Sms.query.filter_by(recipient=auth.get_user().id):
            Proverka = True

        return render_template('sms.html', title='SMS', Proverka=Proverka)

    @app.route('/sms-1', methods=['GET', 'POST'])
    def sms_1():
        form = SmsSee()
        if form.validate_on_submit():
            recipient = form.recipient.data
            text = form.text.data

            Sms.add(recipient=recipient, user=auth.get_user(), text=text)

            return redirect('/sms')
        return render_template(
            'sms-new.html',
            title='Отправка сообщений',
            form=form,
        )

