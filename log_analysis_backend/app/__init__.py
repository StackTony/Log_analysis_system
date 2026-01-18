import os
from flask import Flask
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from pymongo import MongoClient
from celery import Celery
from .config import config

# 初始化扩展
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()

# 初始化MongoDB
mongo_client = None
db_mongo = None

# 初始化Celery
celery = Celery(__name__)

# 创建应用工厂
def create_app(config_name=None):
    if config_name is None:
        config_name = os.environ.get('FLASK_CONFIG') or 'default'
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # 初始化扩展
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    
    # 初始化MongoDB
    global mongo_client, db_mongo
    mongo_client = MongoClient(app.config['MONGODB_URI'])
    db_mongo = mongo_client[app.config['MONGODB_URI'].split('/')[-1]]
    
    # 配置Celery
    celery.conf.update(app.config)
    
    # 创建API实例
    api = Api(app)
    
    # 注册蓝图和路由
    from .api import auth, user, check_item, case, log, report
    
    # 认证路由
    api.add_resource(auth.Register, '/api/auth/register')
    api.add_resource(auth.Login, '/api/auth/login')
    api.add_resource(auth.RefreshToken, '/api/auth/refresh')
    api.add_resource(auth.Logout, '/api/auth/logout')
    
    # 用户路由
    api.add_resource(user.UserList, '/api/users')
    api.add_resource(user.User, '/api/users/<int:user_id>')
    
    # 检查项路由
    api.add_resource(check_item.CheckItemList, '/api/check-items')
    api.add_resource(check_item.CheckItem, '/api/check-items/<int:item_id>')
    
    # 案例路由
    api.add_resource(case.CaseList, '/api/cases')
    api.add_resource(case.Case, '/api/cases/<int:case_id>')
    api.add_resource(case.CaseMerge, '/api/cases/merge')
    
    # 日志路由
    api.add_resource(log.LogCollect, '/api/logs/collect')
    api.add_resource(log.LogUpload, '/api/logs/upload')
    api.add_resource(log.LogReceive, '/api/logs/receive')
    api.add_resource(log.LogList, '/api/logs')
    api.add_resource(log.Log, '/api/logs/<string:log_id>')
    
    # 分析路由
    api.add_resource(report.AnalysisStart, '/api/analysis/start')
    api.add_resource(report.AnalysisResult, '/api/analysis/<int:analysis_id>')
    api.add_resource(report.ReportDetail, '/api/analysis/report/<int:report_id>')
    api.add_resource(report.ReportExport, '/api/analysis/report/export')
    
    return app