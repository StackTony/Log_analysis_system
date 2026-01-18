from flask import request, current_app
from flask_restful import Resource
from app import db, db_mongo
from app.models.report import AnalysisReport
from app.services.analysis_service import analysis_service
from app.services.ai_analysis_service import ai_analysis_service
from app.utils.auth_utils import role_required, get_current_user
from bson import ObjectId
from datetime import datetime

class AnalysisStart(Resource):
    @role_required('user')
    def post(self):
        data = request.get_json()
        
        # 检查必填字段
        if 'log_id' not in data:
            return {'message': 'Missing log_id field'}, 400
        
        log_id = data['log_id']
        
        try:
            # 开始分析日志
            result, status_code = analysis_service.analyze_log(log_id)
            return result, status_code
        except Exception as e:
            return {'message': f'Analysis failed: {str(e)}'}, 500

class AnalysisResult(Resource):
    @role_required('user')
    def get(self, analysis_id):
        # 获取分析结果
        report = AnalysisReport.query.get(analysis_id)
        if not report:
            return {'message': 'Analysis report not found'}, 404
        
        current_user = get_current_user()
        
        # 检查权限
        if current_user.role != 'admin' and report.user_id != current_user.id:
            return {'message': 'Permission denied'}, 403
        
        # 获取日志内容
        log = db_mongo.logs.find_one({'_id': ObjectId(report.log_id)})
        if not log:
            return {'message': 'Log not found'}, 404
        
        # 获取相关案例
        from app.models.case import Case
        cases = Case.query.filter_by(log_id=report.log_id).all()
        
        # 构建响应
        response = {
            'report': report.to_dict(),
            'log_content': log['content'],
            'cases': [case.to_dict() for case in cases]
        }
        
        return response, 200

class ReportDetail(Resource):
    @role_required('user')
    def get(self, report_id):
        # 获取分析报告
        from app.models.report import AnalysisReport
        report = AnalysisReport.query.get(report_id)
        if not report:
            return {'message': 'Analysis report not found'}, 404
        
        current_user = get_current_user()
        
        # 检查权限
        if current_user.role != 'admin' and report.user_id != current_user.id:
            return {'message': 'Permission denied'}, 403
        
        # 获取日志内容
        log = db_mongo.logs.find_one({'_id': ObjectId(report.log_id)})
        if not log:
            return {'message': 'Log not found'}, 404
        
        # 获取相关案例
        from app.models.case import Case
        cases = Case.query.filter_by(log_id=report.log_id).all()
        
        # AI分析结果
        ai_analysis = ai_analysis_service.analyze_log(log['content'])
        ai_summary = ai_analysis_service.generate_summary(log['content'])
        ai_anomalies = ai_analysis_service.detect_anomalies(log['content'])
        
        # 构建响应
        response = {
            'report': report.to_dict(),
            'log_content': log['content'],
            'cases': [case.to_dict() for case in cases],
            'ai_analysis': ai_analysis,
            'ai_summary': ai_summary,
            'ai_anomalies': ai_anomalies
        }
        
        return response, 200

class ReportExport(Resource):
    @role_required('user')
    def post(self):
        data = request.get_json()
        
        # 检查必填字段
        if 'report_id' not in data:
            return {'message': 'Missing report_id field'}, 400
        
        report_id = data['report_id']
        format_type = data.get('format', 'pdf')  # pdf/excel
        
        report = AnalysisReport.query.get(report_id)
        if not report:
            return {'message': 'Analysis report not found'}, 404
        
        current_user = get_current_user()
        
        # 检查权限
        if current_user.role != 'admin' and report.user_id != current_user.id:
            return {'message': 'Permission denied'}, 403
        
        try:
            # TODO: 实现报告导出功能
            # 这里可以使用第三方库如reportlab生成PDF，或使用pandas生成Excel
            
            return {
                'message': 'Report export functionality not yet implemented',
                'report_id': report_id,
                'format': format_type
            }, 200
            
        except Exception as e:
            return {'message': f'Export failed: {str(e)}'}, 500