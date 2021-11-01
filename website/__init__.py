from flask import Flask


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'anything'

    from .views import views
    from .inboxMail import inboxMail
    from .compose import compose

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(compose, url_prefix='/')
    app.register_blueprint(inboxMail, url_prefix='/')

    return app
