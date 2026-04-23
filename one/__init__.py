from flask import Flask, redirect, url_for
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail

import os
import config

mail = Mail()
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager() # 추가됨: 이 줄이 있어야 빨간 줄이 사라집니다.

def create_app():
    app=Flask(__name__)
    app.config.from_object(config)

    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = 'your_email@gmail.com'
    app.config['MAIL_PASSWORD'] = 'omgjqneijyodwlyh'
    app.config['MAIL_DEFAULT_SENDER'] = 'your_email@gmail.com'

    mail.init_app(app)

    # 콘텐츠 파일 업로드 설정
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    app.config['UPLOAD_FOLDER_VIDEOS'] = os.path.join(BASE_DIR, 'static', 'uploads', 'videos')
    app.config['UPLOAD_FOLDER_THUMBNAILS'] = os.path.join(BASE_DIR, 'static', 'uploads', 'thumbnails')
    app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB

    # ORM
    db.init_app(app)
    migrate.init_app(app, db)
    from . import models

    # 3. LoginManager 연결
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'  # 로그인 안됐을 때 이동할 뷰 (선택 사항)

    #블루프린트 목록 이쪽으로 등록해주세요

    from .views import mypage_views,main_views,policy_views,auth_views, admin_views,sub_views,video_views



    app.register_blueprint(mypage_views.bp)
    app.register_blueprint(main_views.bp)
    app.register_blueprint(policy_views.bp)
    app.register_blueprint(auth_views.bp)
    app.register_blueprint(admin_views.bp)
    app.register_blueprint(sub_views.bp)
    app.register_blueprint(video_views.bp)

    # 필터 등록
    from .filters import format_datetime
    app.jinja_env.filters['datetime'] = format_datetime

    @app.route('/')
    def index():
        return redirect(url_for('main.home'))

    return app
