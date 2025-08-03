-- -- 登录MySQL
-- mysql -u xuesong -p

-- 创建数据库
CREATE DATABASE pv_resource_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 使用数据库
USE pv_resource_db;

-- 创建用户表
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    email VARCHAR(100),
    role ENUM('admin', 'user') DEFAULT 'user',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 创建应用用户（用于Python连接）
CREATE USER 'pv_app'@'localhost' IDENTIFIED BY 'your_secure_password';
GRANT SELECT, INSERT, UPDATE, DELETE ON pv_resource_db.* TO 'pv_app'@'localhost';
FLUSH PRIVILEGES;

-- 插入默认管理员用户（密码需要在Python中加密后插入）
-- 这里先创建表结构，用户数据通过Python脚本插入

