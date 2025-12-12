-- 换热器在线监测系统数据库创建脚本
CREATE DATABASE heat_exchanger_monitor_db
    DEFAULT CHARACTER SET = 'utf8mb4'
    DEFAULT COLLATE = 'utf8mb4_unicode_ci';

-- 创建用户 heatexMCP，密码为 123123
CREATE USER 'heatexMCP'@'localhost' IDENTIFIED BY '123123';
CREATE USER 'heatexMCP'@'%' IDENTIFIED BY '123123';

-- 授权用户只能访问 heat_exchanger_monitor_db 数据库的所有权限
GRANT ALL PRIVILEGES ON heat_exchanger_monitor_db.* TO 'heatexMCP'@'localhost';
GRANT ALL PRIVILEGES ON heat_exchanger_monitor_db.* TO 'heatexMCP'@'%';

-- 刷新权限
FLUSH PRIVILEGES;

-- 显示创建的数据库
SHOW DATABASES;

-- 显示所有用户名
SELECT user FROM mysql.user;
