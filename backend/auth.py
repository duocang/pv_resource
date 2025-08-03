import bcrypt
from database import db_config
from mysql.connector import Error

class UserAuth:
    """用户认证类"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """加密密码"""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        """验证密码"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    
    @staticmethod
    def create_user(username: str, password: str, email: str = None, role: str = 'user') -> bool:
        """创建新用户"""
        try:
            hashed_password = UserAuth.hash_password(password)
            
            with db_config.get_connection() as conn:
                cursor = conn.cursor()
                query = """
                    INSERT INTO users (username, password_hash, email, role) 
                    VALUES (%s, %s, %s, %s)
                """
                cursor.execute(query, (username, hashed_password, email, role))
                conn.commit()
                return True
                
        except Error as e:
            print(f"创建用户失败: {e}")
            return False
    
    @staticmethod
    def authenticate_user(username: str, password: str) -> dict:
        """验证用户凭据"""
        try:
            with db_config.get_connection() as conn:
                cursor = conn.cursor(dictionary=True)
                query = """
                    SELECT id, username, password_hash, email, role, is_active 
                    FROM users 
                    WHERE username = %s AND is_active = TRUE
                """
                cursor.execute(query, (username,))
                user = cursor.fetchone()
                
                if user and UserAuth.verify_password(password, user['password_hash']):
                    # 移除密码哈希，返回安全的用户信息
                    del user['password_hash']
                    return user
                    
                return None
                
        except Error as e:
            print(f"用户认证失败: {e}")
            return None
    
    @staticmethod
    def get_user_by_id(user_id: int) -> dict:
        """根据ID获取用户信息"""
        try:
            with db_config.get_connection() as conn:
                cursor = conn.cursor(dictionary=True)
                query = """
                    SELECT id, username, email, role, is_active, created_at 
                    FROM users 
                    WHERE id = %s AND is_active = TRUE
                """
                cursor.execute(query, (user_id,))
                return cursor.fetchone()
                
        except Error as e:
            print(f"获取用户信息失败: {e}")
            return None
    
    @staticmethod
    def update_password(username: str, old_password: str, new_password: str) -> bool:
        """更新用户密码"""
        try:
            # 先验证旧密码
            user = UserAuth.authenticate_user(username, old_password)
            if not user:
                return False
            
            # 更新新密码
            hashed_password = UserAuth.hash_password(new_password)
            
            with db_config.get_connection() as conn:
                cursor = conn.cursor()
                query = "UPDATE users SET password_hash = %s WHERE username = %s"
                cursor.execute(query, (hashed_password, username))
                conn.commit()
                return cursor.rowcount > 0
                
        except Error as e:
            print(f"更新密码失败: {e}")
            return False

# 保持向后兼容的函数
def authenticate_user(username: str, password: str) -> bool:
    """验证用户凭据（向后兼容）"""
    user = UserAuth.authenticate_user(username, password)
    return user is not None