from flask import request
from flask_restful import Resource
from app import db
from app.models.check_item import CheckItem
from app.utils.auth_utils import role_required, get_current_user

class CheckItemList(Resource):
    @role_required('user')
    def get(self):
        # 获取检查项列表
        current_user = get_current_user()
        
        # 管理员可以查看所有检查项，普通用户只能查看自己创建的或公开的
        query = CheckItem.query
        if current_user.role != 'admin':
            query = query.filter_by(created_by=current_user.id)
        
        # 分页参数
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        
        check_items = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return {
            'check_items': [item.to_dict() for item in check_items.items],
            'total': check_items.total,
            'page': check_items.page,
            'per_page': check_items.per_page,
            'pages': check_items.pages
        }, 200
    
    @role_required('admin')
    def post(self):
        # 创建检查项（仅管理员）
        data = request.get_json()
        
        # 检查必填字段
        if not all(k in data for k in ['name', 'rule', 'rule_type', 'severity']):
            return {'message': 'Missing required fields'}, 400
        
        current_user = get_current_user()
        
        try:
            check_item = CheckItem(
                name=data['name'],
                description=data.get('description', ''),
                rule=data['rule'],
                rule_type=data['rule_type'],
                severity=data['severity'],
                created_by=current_user.id
            )
            
            db.session.add(check_item)
            db.session.commit()
            
            return {
                'message': 'Check item created successfully',
                'check_item': check_item.to_dict()
            }, 201
            
        except Exception as e:
            db.session.rollback()
            return {'message': f'Error creating check item: {str(e)}'}, 500

class CheckItem(Resource):
    @role_required('user')
    def get(self, item_id):
        # 获取检查项详情
        current_user = get_current_user()
        check_item = CheckItem.query.get(item_id)
        
        if not check_item:
            return {'message': 'Check item not found'}, 404
        
        # 检查权限
        if current_user.role != 'admin' and check_item.created_by != current_user.id:
            return {'message': 'Permission denied'}, 403
        
        return {'check_item': check_item.to_dict()}, 200
    
    @role_required('admin')
    def put(self, item_id):
        # 更新检查项（仅管理员）
        data = request.get_json()
        check_item = CheckItem.query.get(item_id)
        
        if not check_item:
            return {'message': 'Check item not found'}, 404
        
        try:
            # 更新字段
            if 'name' in data:
                check_item.name = data['name']
            if 'description' in data:
                check_item.description = data['description']
            if 'rule' in data:
                check_item.rule = data['rule']
            if 'rule_type' in data:
                check_item.rule_type = data['rule_type']
            if 'severity' in data:
                check_item.severity = data['severity']
            
            db.session.commit()
            
            return {
                'message': 'Check item updated successfully',
                'check_item': check_item.to_dict()
            }, 200
            
        except Exception as e:
            db.session.rollback()
            return {'message': f'Error updating check item: {str(e)}'}, 500
    
    @role_required('admin')
    def delete(self, item_id):
        # 删除检查项（仅管理员）
        check_item = CheckItem.query.get(item_id)
        
        if not check_item:
            return {'message': 'Check item not found'}, 404
        
        try:
            db.session.delete(check_item)
            db.session.commit()
            return {'message': 'Check item deleted successfully'}, 200
        except Exception as e:
            db.session.rollback()
            return {'message': f'Error deleting check item: {str(e)}'}, 500