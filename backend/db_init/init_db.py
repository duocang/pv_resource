#!/usr/bin/env python3
"""数据库初始化脚本"""

import sys
import os

# 添加父目录到 Python 路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from auth import UserAuth
from database import db_config

def init_database():
    """初始化数据库，创建默认用户"""
    print("正在初始化数据库...")
    
    # 测试数据库连接
    if not db_config.test_connection():
        print("❌ 数据库连接失败，请检查配置")
        return False
    
    print("✅ 数据库连接成功")
    
    # 创建默认管理员用户
    if UserAuth.create_user('admin', 'admin123', 'admin@example.com', 'admin'):
        print("✅ 默认管理员用户创建成功 (用户名: admin, 密码s: admin123)")
    else:
        print("⚠️  管理员用户可能已存在")
    
    # 创建默认普通用户
    if UserAuth.create_user('users', 'user123?', 'user@example.com', 'user'):
        print("✅ 默认普通用户创建成功 (用户名: user, 密码: user123)")
    else:
        print("⚠️  普通用户可能已存在")
    
    print("🎉 数据库初始化完成！")
    return True

if __name__ == '__main__':
    init_database()