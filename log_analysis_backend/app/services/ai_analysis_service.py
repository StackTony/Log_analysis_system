import os
import requests
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class AIAnalysisService:
    def __init__(self):
        # 初始化DeepSeek API密钥
        self.api_key = os.environ.get('DEEPSEEK_API_KEY')
        self.api_url = "https://api.deepseek.com/v1/chat/completions"
        self.enabled = False
        
        if self.api_key:
            try:
                # 测试API连接
                self.enabled = True
            except Exception as e:
                print(f"Failed to initialize DeepSeek API: {str(e)}")
                self.enabled = False
        else:
            print("DeepSeek API key not found in environment variables, AI features will be disabled")
            self.enabled = False
    
    def analyze_log(self, log_content):
        """
        分析日志内容，识别异常模式和潜在问题
        :param log_content: 日志内容
        :return: 分析结果
        """
        if not self.enabled:
            return "AI分析功能未启用，请配置DeepSeek API密钥"
            
        try:
            # 使用DeepSeek模型进行分析
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "deepseek-chat",
                "messages": [
                    {
                        "role": "system",
                        "content": "你是一名日志分析专家，擅长识别日志中的异常模式、错误信息和潜在问题。请分析以下日志内容，提供详细的分析结果，包括发现的问题、严重程度评估和解决方案建议。"
                    },
                    {
                        "role": "user",
                        "content": log_content
                    }
                ],
                "max_tokens": 1000,
                "temperature": 0.5
            }
            
            response = requests.post(self.api_url, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            
            return response.json()['choices'][0]['message']['content'].strip()
            
        except Exception as e:
            return f"AI分析失败: {str(e)}"
    
    def generate_summary(self, log_content):
        """
        生成日志摘要，提取关键信息
        :param log_content: 日志内容
        :return: 日志摘要
        """
        if not self.enabled:
            return "AI摘要功能未启用，请配置DeepSeek API密钥"
            
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "deepseek-chat",
                "messages": [
                    {
                        "role": "system",
                        "content": "请为以下日志内容生成简洁的摘要，提取关键信息，包括时间范围、主要事件、错误信息和系统状态。"
                    },
                    {
                        "role": "user",
                        "content": log_content
                    }
                ],
                "max_tokens": 500,
                "temperature": 0.3
            }
            
            response = requests.post(self.api_url, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            
            return response.json()['choices'][0]['message']['content'].strip()
            
        except Exception as e:
            return f"摘要生成失败: {str(e)}"
    
    def query_log(self, log_content, query):
        """
        使用自然语言查询日志内容
        :param log_content: 日志内容
        :param query: 查询语句
        :return: 查询结果
        """
        if not self.enabled:
            return "AI查询功能未启用，请配置DeepSeek API密钥"
            
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "deepseek-chat",
                "messages": [
                    {
                        "role": "system",
                        "content": "请根据以下查询，从提供的日志内容中提取相关信息，提供准确、简洁的回答。"
                    },
                    {
                        "role": "user",
                        "content": f"日志内容：{log_content}\n\n查询：{query}"
                    }
                ],
                "max_tokens": 800,
                "temperature": 0.3
            }
            
            response = requests.post(self.api_url, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            
            return response.json()['choices'][0]['message']['content'].strip()
            
        except Exception as e:
            return f"查询失败: {str(e)}"
    
    def detect_anomalies(self, log_content):
        """
        检测日志中的异常模式
        :param log_content: 日志内容
        :return: 异常检测结果
        """
        if not self.enabled:
            return "AI异常检测功能未启用，请配置DeepSeek API密钥"
            
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "deepseek-chat",
                "messages": [
                    {
                        "role": "system",
                        "content": "请分析以下日志内容，识别其中的异常模式、错误、警告或不寻常的活动。请列出每个异常的类型、位置和可能的原因。"
                    },
                    {
                        "role": "user",
                        "content": log_content
                    }
                ],
                "max_tokens": 1000,
                "temperature": 0.5
            }
            
            response = requests.post(self.api_url, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            
            return response.json()['choices'][0]['message']['content'].strip()
            
        except Exception as e:
            return f"异常检测失败: {str(e)}"

# 创建AI分析服务实例
ai_analysis_service = AIAnalysisService()