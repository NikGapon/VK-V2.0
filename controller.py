from flask_restful import abort

from flask import redirect, request, flash, session
from flask import render_template as flask_render_template
import extra.auth as auth
from api.v1 import init as init_api_v1
from forms import UserCreateForm, NewsCreateForm, EditProfileForm, LoginForm

from models import User, News


def init_route(app, db):

    # Переопределение стандартного рендера, добавляет параметр auth_user
    def render_template(*args, **kwargs):
        kwargs['auth_user'] = auth.get_user()
        return flask_render_template(*args, **kwargs)

    init_api_v1(app, auth)  # Инициализация маршрутов для API

    @app.route('/')
    @app.route('/index')
    def index():
        if not auth.is_authorized():
            return render_template(
                'index.html',
                title='Главная',
            )
        news_list = News.query.filter_by(user_id=auth.get_user().id)
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
                username = request.form['username']

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
    def dbemty():
        return render_template(
            'dbempty.html',
            title='Пользователей нет')

    @app.route('/user/create', methods=['GET', 'POST'])
    def registration():

        db.create_all()
        has_error = False
        form = UserCreateForm()
        if form.validate_on_submit():
            username = form.username.data
            password = form.password.data
            user = User.query.filter_by(username=username).first()
            if user:
                has_error = True
            else:
                User.add(username=username, password=password)
                auth.login(username, password)
                return redirect('/')
        return render_template(
            'registration.html',
            title='Зарегистрироваться',
            form=form,
            has_error=has_error
        )

    @app.route('/news', methods=['GET'])
    def news_list():
        if not auth.is_authorized():
            return redirect('/login')
        news_list = News.query.filter_by(user_id=auth.get_user().id)
        return render_template(
            'news-list.html',
            title="Новости",
            news_list=news_list
        )

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
        if not auth.is_authorized():
            return redirect('/login')
        news = News.query.filter_by(id=id).first()
        if not news:
            abort(404)
        if news.user_id != auth.get_user().id:
            abort(403)
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
        if form.validate_on_submit():
            user = auth.get_user()
            username = form.username.data
            password = form.password.data
            users = User.query.filter_by(username=username).first()
            if users:
                has_error = True
            elif not has_error:
                user.username = username
                user.password = password
                db.session.commit()
                return redirect('/success')
        return render_template(
            'edit_profile.html',
            title='Редактировать профиль',
            form=form,
            has_error=has_error
        )
