# 简单的用户认证模块
# 在生产环境中，应该使用数据库存储用户信息并加密密码

USERS = {
    'admin': 'admin123',
    'user': 'user123'
}

def authenticate_user(username, password):
    """验证用户凭据"""
    return USERS.get(username) == password