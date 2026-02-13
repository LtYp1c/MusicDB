from flask import Flask, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 数据库配置
# 使用PyMySQL替代MySQLdb
import pymysql
pymysql.install_as_MySQLdb()

app = Flask(__name__)
CORS(app)  # 允许跨域请求

# 从环境变量获取配置
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '3306')
DB_USERNAME = os.getenv('DB_USERNAME', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'password')
DB_NAME = os.getenv('DB_NAME', 'musicdb')

# 构建数据库连接字符串
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 导入并初始化数据库
from models import db
db.init_app(app)

# 导入路由
from routes import api
app.register_blueprint(api, url_prefix='/api')

# 创建数据库表
with app.app_context():
    db.create_all()

# 根路由
@app.route('/')
def index():
    return jsonify({
        'message': '音乐数据库API',
        'version': '1.0.0',
        'endpoints': {
            'users': '/api/users',
            'singers': '/api/singers',
            'albums': '/api/albums',
            'songs': '/api/songs',
            'favorites': '/api/favorites'
        }
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)