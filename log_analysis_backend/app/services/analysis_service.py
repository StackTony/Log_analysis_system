import re
from datetime import datetime
from bson import ObjectId
from app import db, db_mongo
from app.models.check_item import CheckItem
from app.models.case import Case
from app.models.report import AnalysisReport
from app.services.ai_analysis_service import ai_analysis_service
from app.utils.auth_utils import get_current_user

class AnalysisService:
    def __init__(self):
        pass
    
    def match_check_items(self, log_content):
        """
        匹配日志内容与检查项
        :param log_content: 日志内容
        :return: 匹配结果列表
        """
        match_results = []
        
        # 获取所有检查项
        check_items = CheckItem.query.all()
        
        for item in check_items:
            if item.rule_type == 'regex':
                # 使用正则表达式匹配
                try:
                    matches = re.findall(item.rule, log_content, re.MULTILINE)
                    if matches:
                        match_results.append({
                            'check_item': item,
                            'matches': matches
                        })
                except re.error as e:
                    print(f"正则表达式错误 (ID: {item.id}): {str(e)}")
            elif item.rule_type == 'keyword':
                # 使用关键词匹配
                if item.rule in log_content:
                    match_results.append({
                        'check_item': item,
                        'matches': [item.rule]
                    })
        
        return match_results
    
    def analyze_log(self, log_id):
        """
        分析日志
        :param log_id: 日志ID
        :return: 分析报告
        """
        current_user = get_current_user()
        
        # 从MongoDB获取日志
        log = db_mongo.logs.find_one({'_id': ObjectId(log_id)})
        if not log:
            return {'message': 'Log not found'}, 404
        
        log_content = log['content']
        
        try:
            # 匹配检查项
            match_results = self.match_check_items(log_content)
            
            # AI分析
            ai_analysis = ai_analysis_service.analyze_log(log_content)
            ai_summary = ai_analysis_service.generate_summary(log_content)
            ai_anomalies = ai_analysis_service.detect_anomalies(log_content)
            
            # 创建分析报告
            report = AnalysisReport(
                user_id=current_user.id,
                log_id=str(log_id),
                analysis_time=datetime.utcnow(),
                result_summary=f"匹配到 {len(match_results)} 个检查项\n\nAI摘要：{ai_summary}",
                status='success'
            )
            
            db.session.add(report)
            db.session.commit()
            
            # 处理案例
            for result in match_results:
                check_item = result['check_item']
                
                # 创建案例
                case = Case(
                    check_item_id=check_item.id,
                    log_id=str(log_id),
                    log_content=log_content,
                    analysis_result=f"匹配规则：{check_item.rule}\n\n匹配内容：{str(result['matches'])}\n\nAI分析：{ai_analysis}",
                    status='pending',
                    processed_by=current_user.id
                )
                
                db.session.add(case)
            
            db.session.commit()
            
            # 构建分析结果
            analysis_result = {
                'report_id': report.id,
                'log_id': str(log_id),
                'match_count': len(match_results),
                'matches': [{
                    'check_item_id': result['check_item'].id,
                    'check_item_name': result['check_item'].name,
                    'check_item_severity': result['check_item'].severity,
                    'matches': result['matches']
                } for result in match_results],
                'ai_analysis': ai_analysis,
                'ai_summary': ai_summary,
                'ai_anomalies': ai_anomalies,
                'analysis_time': report.analysis_time.isoformat()
            }
            
            return analysis_result, 200
            
        except Exception as e:
            db.session.rollback()
            return {'message': f'Analysis failed: {str(e)}'}, 500
    
    def get_analysis_report(self, report_id):
        """
        获取分析报告
        :param report_id: 报告ID
        :return: 分析报告
        """
        report = AnalysisReport.query.get(report_id)
        if not report:
            return {'message': 'Report not found'}, 404
        
        # 获取相关案例
        cases = Case.query.filter_by(log_id=report.log_id).all()
        
        # 获取日志内容
        log = db_mongo.logs.find_one({'_id': ObjectId(report.log_id)})
        if not log:
            return {'message': 'Log not found'}, 404
        
        # 构建报告内容
        report_content = {
            'report': report.to_dict(),
            'log_content': log['content'],
            'cases': [case.to_dict() for case in cases]
        }
        
        return report_content, 200

# 创建分析服务实例
analysis_service = AnalysisService()