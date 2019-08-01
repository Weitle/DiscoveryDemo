import os
from flask import Flask

from app.models import Product, Channel, IncomeType

USERNAME = os.getenv('USERNAME')
PASSWORD = os.getenv('PASSWORD')
HOSTNAME = os.getenv('HOSTNAME')
DBNAME = os.getenv('DBNAME')
db_url = "mysql+pymysql://%s:%s@%s/%s?charset=utf8mb4" % (USERNAME, PASSWORD, HOSTNAME, DBNAME)
def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = b'\xb3x\xc8^\xa3K\x0bY\xe7\xc6\x7f\xbc\x97\xb4v\xc1\x00\x82h\xbe\xf5\x9aZesS\xa5\x7f\xa9\x1bZ\x08'
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url
    app.config['SQLCHEMY_COMMIT_ON_TEARDOWN'] = True

    # 引入管理组件
    from .db import db
    db.init_app(app)
    from .migrate import migrate
    migrate.init_app(app)
    from .exts import csrf
    csrf.init_app(app)
    
    # 注册蓝图
    from .auth import auth as auth
    app.register_blueprint(auth)
    from .forecast import forecast
    app.register_blueprint(forecast)
    from .competition import competition
    app.register_blueprint(competition)
    from .indicator import indicator
    app.register_blueprint(indicator)
    from .admin import admin
    app.register_blueprint(admin)
    from .analysis import analysis
    app.register_blueprint(analysis)
    from .api import api
    app.register_blueprint(api)

    return app