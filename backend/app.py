from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from datetime import timedelta
import threading
import time
from system_monitor import SystemMonitor
from auth import authenticate_user

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'your-secret-key-change-in-production'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)

# 启用CORS
CORS(app)

# 初始化JWT
jwt = JWTManager(app)

# 初始化系统监控器
system_monitor = SystemMonitor()

# 启动后台监控线程
def start_monitoring():
    system_monitor.start_monitoring()

monitoring_thread = threading.Thread(target=start_monitoring, daemon=True)
monitoring_thread.start()

@app.route('/api/login', methods=['POST'])
def login():
    """用户登录接口"""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if authenticate_user(username, password):
        access_token = create_access_token(identity=username)
        return jsonify({
            'success': True,
            'token': access_token,
            'message': '登录成功'
        })
    else:
        return jsonify({
            'success': False,
            'message': '用户名或密码错误'
        }), 401

@app.route('/api/system-status', methods=['GET'])
@jwt_required()
def get_system_status():
    """获取系统状态信息"""
    try:
        status = system_monitor.get_current_status()
        return jsonify({
            'success': True,
            'data': status
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取系统状态失败: {str(e)}'
        }), 500

@app.route('/api/system-history', methods=['GET'])
@jwt_required()
def get_system_history():
    """获取系统历史数据"""
    try:
        history = system_monitor.get_history_data()
        return jsonify({
            'success': True,
            'data': history
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取历史数据失败: {str(e)}'
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    return jsonify({
        'success': True,
        'message': 'API服务正常运行'
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)