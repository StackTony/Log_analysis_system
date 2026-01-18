from flask import request
from flask_restful import Resource
from flask_bcrypt import Bcrypt
from app import db
from app.models.user import User
from app.utils.auth_utils import role_required, get_current_user

# 创建Bcrypt实例
bcrypt = Bcrypt()

class UserList(Resource):
    @role_required('admin')
    def get(self):
        # 获取所有用户（仅管理员）
        users = User.query.all()
        return {'users': [user.to_dict() for user in users]}, 200
    
    @role_required('admin')
    def post(self):
        # 创建新用户（仅管理员）
        data = request.get_json()
        
        # 检查必填字段
        if not all(k in data for k in ['username', 'password', 'email']):
            return {'message': 'Missing required fields'}, 400
        
        # 检查用户名是否已存在
        if User.query.filter_by(username=data['username']).first():
            return {'message': 'Username already exists'}, 400
        
        # 检查邮箱是否已存在
        if User.query.filter_by(email=data['email']).first():
            return {'message': 'Email already exists'}, 400
        
        # 创建新用户
        try:
            user = User(
                username=data['username'],
                password=data['password'],
                email=data['email'],
                role=data.get('role', 'user')
            )
            db.session.add(user)
            db.session.commit()
            return {'message': 'User created successfully', 'user': user.to_dict()}, 201
        except Exception as e:
            db.session.rollback()
            return {'message': f'Error creating user: {str(e)}'}, 500

class User(Resource):
    @role_required('user')
    def get(self, user_id):
        # 获取用户详情
        current_user = get_current_user()
        
        # 管理员可以查看所有用户，普通用户只能查看自己
        if current_user.role != 'admin' and current_user.id != user_id:
            return {'message': 'Permission denied'}, 403
        
        user = User.query.get(user_id)
        if not user:
            return {'message': 'User not found'}, 404
        
        return {'user': user.to_dict()}, 200
    
    @role_required('user')
    def put(self, user_id):
        # 更新用户信息
        current_user = get_current_user()
        
        # 管理员可以更新所有用户，普通用户只能更新自己
        if current_user.role != 'admin' and current_user.id != user_id:
            return {'message': 'Permission denied'}, 403
        
        user = User.query.get(user_id)
        if not user:
            return {'message': 'User not found'}, 404
        
        data = request.get_json()
        
        # 检查用户名是否已存在（如果要更新用户名）
        if 'username' in data and data['username'] != user.username:
            if User.query.filter_by(username=data['username']).first():
                return {'message': 'Username already exists'}, 400
            user.username = data['username']
        
        # 检查邮箱是否已存在（如果要更新邮箱）
        if 'email' in data and data['email'] != user.email:
            if User.query.filter_by(email=data['email']).first():
                return {'message': 'Email already exists'}, 400
            user.email = data['email']
        
        # 更新密码（如果提供）
        if 'password' in data:
            user.password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
        
        # 更新角色（仅管理员）
        if 'role' in data:
            if current_user.role != 'admin':
                return {'message': 'Only admin can update role'}, 403
            user.role = data['role']
        
        try:
            db.session.commit()
            return {'message': 'User updated successfully', 'user': user.to_dict()}, 200
        except Exception as e:
            db.session.rollback()
            return {'message': f'Error updating user: {str(e)}'}, 500
    
    @role_required('admin')
    def delete(self, user_id):
        # 删除用户（仅管理员）
        user = User.query.get(user_id)
        if not user:
            return {'message': 'User not found'}, 404
        
        try:
            db.session.delete(user)
            db.session.commit()
            return {'message': 'User deleted successfully'}, 200
        except Exception as e:
            db.session.rollback()
            return {'message': f'Error deleting user: {str(e)}'}, 500