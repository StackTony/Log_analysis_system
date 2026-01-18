from functools import wraps
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.models.user import User

def role_required(required_role):
    """
    角色检查装饰器，确保用户具有指定角色
    :param required_role: 需要的角色（admin/user）
    """
    def decorator(func):
        @wraps(func)
        @jwt_required()
        def wrapper(*args, **kwargs):
            claims = get_jwt()
            user_role = claims.get('role', 'user')
            
            # 管理员可以访问所有资源
            if user_role == 'admin':
                return func(*args, **kwargs)
            
            # 检查用户是否具有所需角色
            if user_role != required_role:
                return {'message': 'Permission denied'}, 403
            
            return func(*args, **kwargs)
        return wrapper
    return decorator

def get_current_user():
    """
    获取当前登录用户
    """
    user_id = get_jwt_identity()
    return User.query.get(user_id)