from flask import request
from flask_restful import Resource
from app import db
from app.models.case import Case
from app.models.check_item import CheckItem
from app.utils.auth_utils import role_required, get_current_user

class CaseList(Resource):
    @role_required('user')
    def get(self):
        current_user = get_current_user()
        
        # 管理员可以查看所有案例，普通用户只能查看自己处理的或与自己相关的
        query = Case.query
        
        # 筛选条件
        check_item_id = request.args.get('check_item_id')
        status = request.args.get('status')
        
        if check_item_id:
            query = query.filter_by(check_item_id=int(check_item_id))
        if status:
            query = query.filter_by(status=status)
        
        # 分页参数
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        
        cases = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return {
            'cases': [case.to_dict() for case in cases.items],
            'total': cases.total,
            'page': cases.page,
            'per_page': cases.per_page,
            'pages': cases.pages
        }, 200

class Case(Resource):
    @role_required('user')
    def get(self, case_id):
        # 获取案例详情
        current_user = get_current_user()
        case = Case.query.get(case_id)
        
        if not case:
            return {'message': 'Case not found'}, 404
        
        # 检查权限
        if current_user.role != 'admin':
            # 普通用户只能查看与自己相关的案例
            if case.processed_by != current_user.id:
                # 检查是否与用户的检查项相关
                check_item = CheckItem.query.get(case.check_item_id)
                if not check_item or check_item.created_by != current_user.id:
                    return {'message': 'Permission denied'}, 403
        
        return {'case': case.to_dict()}, 200
    
    @role_required('admin')
    def put(self, case_id):
        # 更新案例（仅管理员）
        data = request.get_json()
        case = Case.query.get(case_id)
        
        if not case:
            return {'message': 'Case not found'}, 404
        
        try:
            # 更新字段
            if 'analysis_result' in data:
                case.analysis_result = data['analysis_result']
            if 'status' in data:
                case.status = data['status']
            if 'processed_by' in data:
                case.processed_by = data['processed_by']
            
            db.session.commit()
            
            return {
                'message': 'Case updated successfully',
                'case': case.to_dict()
            }, 200
            
        except Exception as e:
            db.session.rollback()
            return {'message': f'Error updating case: {str(e)}'}, 500
    
    @role_required('admin')
    def delete(self, case_id):
        # 删除案例（仅管理员）
        case = Case.query.get(case_id)
        
        if not case:
            return {'message': 'Case not found'}, 404
        
        try:
            db.session.delete(case)
            db.session.commit()
            return {'message': 'Case deleted successfully'}, 200
        except Exception as e:
            db.session.rollback()
            return {'message': f'Error deleting case: {str(e)}'}, 500

class CaseMerge(Resource):
    @role_required('admin')
    def post(self):
        # 合并案例（仅管理员）
        data = request.get_json()
        
        # 检查必填字段
        if 'case_ids' not in data or len(data['case_ids']) < 2:
            return {'message': 'At least two case IDs are required for merging'}, 400
        
        case_ids = data['case_ids']
        
        try:
            # 获取所有要合并的案例
            cases = Case.query.filter(Case.id.in_(case_ids)).all()
            
            if len(cases) != len(case_ids):
                return {'message': 'One or more cases not found'}, 404
            
            # 检查是否属于同一个检查项
            check_item_id = cases[0].check_item_id
            if not all(case.check_item_id == check_item_id for case in cases):
                return {'message': 'All cases must belong to the same check item for merging'}, 400
            
            # 使用第一个案例作为主案例，合并其他案例的内容
            main_case = cases[0]
            merged_content = main_case.log_content
            merged_analysis = main_case.analysis_result or ''
            
            # 合并其他案例的内容
            for case in cases[1:]:
                if case.log_content not in merged_content:
                    merged_content += '\n\n--- 合并的案例内容 ---\n\n' + case.log_content
                if case.analysis_result and case.analysis_result not in merged_analysis:
                    merged_analysis += '\n\n--- 合并的分析结果 ---\n\n' + case.analysis_result
            
            # 更新主案例
            main_case.log_content = merged_content
            main_case.analysis_result = merged_analysis
            main_case.status = 'processed'
            
            # 删除其他案例
            for case in cases[1:]:
                db.session.delete(case)
            
            db.session.commit()
            
            return {
                'message': f'Successfully merged {len(cases)} cases',
                'merged_case': main_case.to_dict()
            }, 200
            
        except Exception as e:
            db.session.rollback()
            return {'message': f'Error merging cases: {str(e)}'}, 500