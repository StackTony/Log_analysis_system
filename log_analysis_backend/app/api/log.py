import os
import subprocess
import uuid
import re
from datetime import datetime
from bson import ObjectId
from flask import request, current_app
from flask_restful import Resource
from werkzeug.utils import secure_filename
from app import db_mongo
from app.utils.auth_utils import role_required, get_current_user

class LogCollect(Resource):
    @role_required('user')
    def post(self):
        data = request.get_json()
        
        # 检查必填字段
        if 'command' not in data:
            return {'message': 'Missing command field'}, 400
        
        current_user = get_current_user()
        command = data['command']
        
        # 安全检查：防止命令注入
        # 仅允许特定命令格式（如tail, cat等）
        allowed_commands = ['tail', 'cat', 'grep', 'dmesg', 'journalctl']
        command_parts = command.split()
        
        if not command_parts or command_parts[0] not in allowed_commands:
            return {'message': 'Command not allowed'}, 403
        
        # 移除可能的危险参数
        sanitized_command = [command_parts[0]]
        for part in command_parts[1:]:
            if not re.search(r'[;|&`$><]', part):
                sanitized_command.append(part)
        
        try:
            # 执行命令收集日志
            result = subprocess.run(
                sanitized_command, 
                shell=False,  # 关闭shell以防止注入
                capture_output=True, 
                text=True,
                timeout=30  # 设置超时时间
            )
            
            if result.returncode != 0:
                return {'message': f'Command execution failed: {result.stderr}'}, 400
            
            # 存储日志到MongoDB
            log_data = {
                'content': result.stdout,
                'source': 'command',
                'collection_time': datetime.utcnow(),
                'user_id': current_user.id,
                'metadata': {
                    'command': ' '.join(sanitized_command),
                    'ip': request.remote_addr,
                    'timestamp': datetime.utcnow()
                },
                'created_at': datetime.utcnow()
            }
            
            log_id = db_mongo.logs.insert_one(log_data).inserted_id
            
            return {
                'message': 'Log collected successfully',
                'log_id': str(log_id),
                'log_content': result.stdout,
                'command': ' '.join(sanitized_command)
            }, 200
            
        except subprocess.TimeoutExpired:
            return {'message': 'Command execution timed out'}, 408
        except Exception as e:
            return {'message': f'Error collecting log: {str(e)}'}, 500

class LogUpload(Resource):
    @role_required('user')
    def post(self):
        # 检查是否有文件上传
        if 'file' not in request.files:
            return {'message': 'No file part'}, 400
        
        file = request.files['file']
        
        # 检查文件名是否为空
        if file.filename == '':
            return {'message': 'No selected file'}, 400
        
        current_user = get_current_user()
        
        try:
            # 保存文件
            filename = secure_filename(file.filename)
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            
            # 读取文件内容
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 存储日志到MongoDB
            log_data = {
                'content': content,
                'source': 'file',
                'collection_time': datetime.utcnow(),
                'user_id': current_user.id,
                'metadata': {
                    'filename': filename,
                    'file_path': file_path,
                    'ip': request.remote_addr,
                    'timestamp': datetime.utcnow()
                },
                'created_at': datetime.utcnow()
            }
            
            log_id = db_mongo.logs.insert_one(log_data).inserted_id
            
            return {
                'message': 'Log uploaded successfully',
                'log_id': str(log_id),
                'filename': filename,
                'file_path': file_path
            }, 200
            
        except UnicodeDecodeError:
            return {'message': 'File must be a text file'}, 400
        except Exception as e:
            return {'message': f'Error uploading log: {str(e)}'}, 500

class LogReceive(Resource):
    @role_required('user')
    def post(self):
        data = request.get_json()
        
        # 检查必填字段
        if 'log_content' not in data:
            return {'message': 'Missing log_content field'}, 400
        
        current_user = get_current_user()
        
        try:
            # 存储日志到MongoDB
            log_data = {
                'content': data['log_content'],
                'source': 'api',
                'collection_time': datetime.utcnow(),
                'user_id': current_user.id,
                'metadata': {
                    'ip': request.remote_addr,
                    'timestamp': datetime.utcnow(),
                    'additional_info': data.get('additional_info', {})
                },
                'created_at': datetime.utcnow()
            }
            
            log_id = db_mongo.logs.insert_one(log_data).inserted_id
            
            return {
                'message': 'Log received successfully',
                'log_id': str(log_id)
            }, 200
            
        except Exception as e:
            return {'message': f'Error receiving log: {str(e)}'}, 500

class LogList(Resource):
    @role_required('user')
    def get(self):
        current_user = get_current_user()
        
        # 管理员可以查看所有日志，普通用户只能查看自己的日志
        query = {}
        if current_user.role != 'admin':
            query['user_id'] = current_user.id
        
        # 分页参数
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        skip = (page - 1) * per_page
        
        try:
            # 查询日志
            logs = list(db_mongo.logs.find(query).skip(skip).limit(per_page).sort('created_at', -1))
            total = db_mongo.logs.count_documents(query)
            
            # 转换为可序列化的格式
            for log in logs:
                log['_id'] = str(log['_id'])
                log['collection_time'] = log['collection_time'].isoformat()
                log['created_at'] = log['created_at'].isoformat()
                if 'timestamp' in log['metadata']:
                    log['metadata']['timestamp'] = log['metadata']['timestamp'].isoformat()
            
            return {
                'logs': logs,
                'total': total,
                'page': page,
                'per_page': per_page
            }, 200
            
        except Exception as e:
            return {'message': f'Error getting logs: {str(e)}'}, 500

class Log(Resource):
    @role_required('user')
    def get(self, log_id):
        current_user = get_current_user()
        
        try:
            # 查询日志
            log = db_mongo.logs.find_one({'_id': ObjectId(log_id)})
            
            if not log:
                return {'message': 'Log not found'}, 404
            
            # 检查权限
            if current_user.role != 'admin' and log['user_id'] != current_user.id:
                return {'message': 'Permission denied'}, 403
            
            # 转换为可序列化的格式
            log['_id'] = str(log['_id'])
            log['collection_time'] = log['collection_time'].isoformat()
            log['created_at'] = log['created_at'].isoformat()
            if 'timestamp' in log['metadata']:
                log['metadata']['timestamp'] = log['metadata']['timestamp'].isoformat()
            
            return {'log': log}, 200
            
        except Exception as e:
            return {'message': f'Error getting log: {str(e)}'}, 500
    
    @role_required('user')
    def delete(self, log_id):
        current_user = get_current_user()
        
        try:
            # 查询日志
            log = db_mongo.logs.find_one({'_id': ObjectId(log_id)})
            
            if not log:
                return {'message': 'Log not found'}, 404
            
            # 检查权限
            if current_user.role != 'admin' and log['user_id'] != current_user.id:
                return {'message': 'Permission denied'}, 403
            
            # 删除日志
            db_mongo.logs.delete_one({'_id': ObjectId(log_id)})
            
            return {'message': 'Log deleted successfully'}, 200
            
        except Exception as e:
            return {'message': f'Error deleting log: {str(e)}'}, 500