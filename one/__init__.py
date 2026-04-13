from flask import Flask, redirect, url_for
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

import config

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app=Flask(__name__)
    app.config.from_object(config)

    # ORM
    db.init_app(app)
    migrate.init_app(app, db)
    from . import models

    #블루프린트 목록 이쪽으로 등록해주세요
    from .views import mypage_views, main_views, policy_views, admin_views

    app.register_blueprint(mypage_views.bp)
    app.register_blueprint(main_views.bp)
    app.register_blueprint(policy_views.bp)
    app.register_blueprint(admin_views.bp)

    @app.route('/')
    def index():
        return redirect(url_for('main.home'))

    return app
