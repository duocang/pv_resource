from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from datetime import timedelta
import threading
import time
from system_monitor import SystemMonitor
from auth import UserAuth
from database import db_config

app = Flask(__name__)
# 在第12行后添加
app.config['JWT_SECRET_KEY'] = 'your-secret-key-change-in-production'
print(f"JWT Secret Key: {app.config['JWT_SECRET_KEY']}")  # 调试信息
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)

# 启用CORS
CORS(app)

# 初始化JWT
jwt = JWTManager(app)

# 添加JWT错误处理器
@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return jsonify({
        'success': False,
        'message': 'Token已过期，请重新登录',
        'error': 'token_expired'
    }), 401

@jwt.invalid_token_loader
def invalid_token_callback(error):
    print(f"JWT Invalid Token Error: {error}")  # 添加调试信息
    return jsonify({
        'success': False,
        'message': 'Token无效，请重新登录',
        'error': 'token_invalid'
    }), 401

@jwt.unauthorized_loader
def missing_token_callback(error):
    return jsonify({
        'success': False,
        'message': '缺少认证Token，请先登录',
        'error': 'token_missing'
    }), 401

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
    
    user = UserAuth.authenticate_user(username, password)
    if user:
        access_token = create_access_token(
            identity=str(user['id']),  # 将整数转换为字符串
            additional_claims={
                'username': user['username'],
                'role': user['role']
            }
        )
        print(access_token)
        print("JWT生成")
        return jsonify({
            'success': True,
            'token': access_token,
            'user': {
                'id': user['id'],
                'username': user['username'],
                'role': user['role'],
                'email': user['email']
            },
            'message': '登录成功'
        })
    else:
        return jsonify({
            'success': False,
            'message': '用户名或密码错误'
        }), 401

@app.route('/api/user/profile', methods=['GET'])
@jwt_required()
def get_user_profile():
    """获取用户信息"""
    user_id = get_jwt_identity()
    user = UserAuth.get_user_by_id(user_id)
    
    if user:
        return jsonify({
            'success': True,
            'user': user
        })
    else:
        return jsonify({
            'success': False,
            'message': '用户不存在'
        }), 404

@app.route('/api/user/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """修改密码"""
    data = request.get_json()
    old_password = data.get('old_password')
    new_password = data.get('new_password')
    
    user_id = get_jwt_identity()
    user = UserAuth.get_user_by_id(user_id)
    
    if not user:
        return jsonify({
            'success': False,
            'message': '用户不存在'
        }), 404
    
    if UserAuth.update_password(user['username'], old_password, new_password):
        return jsonify({
            'success': True,
            'message': '密码修改成功'
        })
    else:
        return jsonify({
            'success': False,
            'message': '原密码错误或修改失败'
        }), 400

@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    db_status = db_config.test_connection()
    return jsonify({
        'status': 'healthy' if db_status else 'unhealthy',
        'database': 'connected' if db_status else 'disconnected',
        'timestamp': time.time()
    })

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)