import os
from flask import Flask

#USERNAME = os.getenv('USERNAME')
#PASSWORD = os.getenv('PASSWORD')
#HOSTNAME = os.getenv('HOSTNAME')
#db_url = "mysql+pymysql://%s:%s@%s/discory_demo?charset=utf8mb4" % (USERNAME, PASSWORD, HOSTNAME)
def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = b'\xb3x\xc8^\xa3K\x0bY\xe7\xc6\x7f\xbc\x97\xb4v\xc1\x00\x82h\xbe\xf5\x9aZesS\xa5\x7f\xa9\x1bZ\x08'
    #app.config['SQLALCHEMY_DATABASE_URI'] = db_url
    #app.config['SQLCHEMY_COMMIT_ON_TEARDOWN'] = True

    # 引入管理组件
    #from .db import db
    #db.init_app(app)
    #from .migrate import migrate
    #migrate.init_app(app)
    from .exts import csrf
    csrf.init_app(app)
    
    # 注册蓝图
    from app.auth import auth as auth
    app.register_blueprint(auth)
    from app.forecast import forecast
    app.register_blueprint(forecast)
    from app.competition import competition
    app.register_blueprint(competition)
    from app.indicator import indicator
    app.register_blueprint(indicator)
    from app.analysis import analysis
    app.register_blueprint(analysis)
    #from app.api import api as api
    #app.register_blueprint(api)

    return app