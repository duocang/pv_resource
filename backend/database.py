import mysql.connector
from mysql.connector import Error
import os
from contextlib import contextmanager
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

class DatabaseConfig:
    """数据库配置类"""
    
    def __init__(self):
        self.config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': int(os.getenv('DB_PORT', 3306)),
            'database': os.getenv('DB_NAME', 'pv_resource_db'),
            'user': os.getenv('DB_USER', 'pv_app'),
            'password': os.getenv('DB_PASSWORD', 'your_secure_password'),
            'charset': 'utf8mb4',
            'autocommit': True
        }
    
    @contextmanager
    def get_connection(self):
        """获取数据库连接的上下文管理器"""
        connection = None
        try:
            connection = mysql.connector.connect(**self.config)
            yield connection
        except Error as e:
            print(f"数据库连接错误: {e}")
            if connection:
                connection.rollback()
            raise
        finally:
            if connection and connection.is_connected():
                connection.close()
    
    def test_connection(self):
        """测试数据库连接"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                return result[0] == 1
        except Error:
            return False

# 全局数据库配置实例
db_config = DatabaseConfig()