from dbase import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), unique=False, nullable=False)
    avatar = db.Column(db.String(120),  unique=False, nullable=False, default='static\default.png')
    email = db.Column(db.String(120), unique=True, nullable=False)
    about_me = db.Column(db.String(1000), unique=False, nullable=False)

    def __repr__(self):
        return '<User {} {}>'.format(self.id, self.username)

    @staticmethod
    def add(username, password, email,  about_me, avatar):
        user = User(username=username, password=password, email=email, about_me=about_me, avatar=avatar)
        db.session.add(user)
        db.session.commit()

    @staticmethod
    def delete(obj):
        db.session.delete(obj)
        db.session.commit()


class Sms(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    recipient = db.Column(db.String(100), unique=True, nullable=False)
    sender = db.Column(db.String(100), unique=True, nullable=False)
    text = db.Column(db.String(1000), unique=False, nullable=False)

    @staticmethod
    def add(recipient, sender, text):
        sms = Sms(recipient=recipient, sender=sender, text=text)
        db.session.add(sms)
        db.session.commit()
        return sms



    @staticmethod
    def delete(obj):
        db.session.delete(obj)
        db.session.commit()


class News(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), unique=False, nullable=False)
    content = db.Column(db.String(80), unique=False, nullable=True)  # пусть текст можно будет оставить пустым
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    # user_id - вторичный ключ, который связывает 2 таблицы
    # Пользователь пишет Новость(их может быть несколько), Новость принадлежит Пользователю, свзяь Один-Ко-Многим
    user = db.relationship('User', backref=db.backref('news_list', lazy=True))
    # ссылка на модель (класс) выше
    # для User возвращает список его новостей по .user_news

    def __repr__(self):
        return '<News {} {} {}>'.format(self.id, self.title, self.user_id)

    @staticmethod
    def add(title, content, user):
        news = News(title=title, content=content, user=user)
        db.session.add(news)
        db.session.commit()
        return news

    @staticmethod
    def delete(obj):
        db.session.delete(obj)
        db.session.commit()

    @property
    def serialize(self):
        """Return object data in easily serializable format"""
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'user_id': self.user_id
        }

