import os
from dotenv import load_dotenv
from app import create_app

# 加载环境变量
load_dotenv()

# 创建应用
app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '0.0.0.0')
    app.run(host=host, port=port)