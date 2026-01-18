from flask import request
from flask_restful import Resource
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity, get_jwt
from app import db
from app.models.user import User

class Register(Resource):
    def post(self):
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

class Login(Resource):
    def post(self):
        data = request.get_json()
        
        # 检查必填字段
        if not all(k in data for k in ['username', 'password']):
            return {'message': 'Missing required fields'}, 400
        
        # 查找用户
        user = User.query.filter_by(username=data['username']).first()
        
        # 验证用户和密码
        if not user or not user.check_password(data['password']):
            return {'message': 'Invalid username or password'}, 401
        
        # 创建Token
        access_token = create_access_token(identity=user.id, additional_claims={'role': user.role})
        refresh_token = create_refresh_token(identity=user.id)
        
        return {
            'message': 'Login successful',
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': user.to_dict()
        }, 200

class RefreshToken(Resource):
    @jwt_required(refresh=True)
    def post(self):
        current_user = get_jwt_identity()
        user = User.query.get(current_user)
        
        if not user:
            return {'message': 'User not found'}, 404
        
        # 创建新的访问Token
        new_access_token = create_access_token(identity=current_user, additional_claims={'role': user.role})
        
        return {
            'message': 'Token refreshed successfully',
            'access_token': new_access_token
        }, 200

class Logout(Resource):
    @jwt_required()
    def post(self):
        # 在实际应用中，可以将Token添加到黑名单
        jti = get_jwt()['jti']
        # 这里应该实现将jti添加到黑名单的逻辑
        
        return {'message': 'Logout successful'}, 200