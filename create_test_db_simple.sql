-- 换热器在线监测系统test数据库创建脚本
-- 简化版，确保语法兼容性

-- 使用root用户登录后执行此脚本

-- 1. 创建test数据库
CREATE DATABASE IF NOT EXISTS heat_exchanger_monitor_db_test
    DEFAULT CHARACTER SET utf8mb4
    DEFAULT COLLATE utf8mb4_unicode_ci;

-- 2. 授权用户访问
GRANT ALL PRIVILEGES ON heat_exchanger_monitor_db_test.* TO 'heatexMCP'@'localhost' IDENTIFIED BY '123123';
GRANT ALL PRIVILEGES ON heat_exchanger_monitor_db_test.* TO 'heatexMCP'@'%' IDENTIFIED BY '123123';
FLUSH PRIVILEGES;

-- 3. 使用test数据库
USE heat_exchanger_monitor_db_test;

-- 4. 创建换热器表
CREATE TABLE heat_exchanger (
    id INT PRIMARY KEY AUTO_INCREMENT,
    type VARCHAR(50) NOT NULL,
    tube_side_fluid VARCHAR(50) NOT NULL,
    shell_side_fluid VARCHAR(50) NOT NULL,
    tube_section_count INT NOT NULL,
    shell_section_count INT NOT NULL,
    d_i_original FLOAT NOT NULL,
    d_o FLOAT NOT NULL,
    lambda_t FLOAT NOT NULL
) ENGINE=InnoDB;

-- 5. 创建运行参数表
CREATE TABLE operation_parameters (
    id INT PRIMARY KEY AUTO_INCREMENT,
    heat_exchanger_id INT NOT NULL,
    timestamp DATETIME NOT NULL,
    points INT NOT NULL,
    side VARCHAR(10) NOT NULL,
    temperature FLOAT,
    pressure FLOAT,
    flow_rate FLOAT,
    velocity FLOAT,
    FOREIGN KEY (heat_exchanger_id) REFERENCES heat_exchanger(id) ON DELETE CASCADE,
    UNIQUE KEY (heat_exchanger_id, timestamp, points, side)
) ENGINE=InnoDB;

-- 6. 创建物性参数表
CREATE TABLE physical_parameters (
    id INT PRIMARY KEY AUTO_INCREMENT,
    heat_exchanger_id INT NOT NULL,
    timestamp DATETIME NOT NULL,
    points INT NOT NULL,
    side VARCHAR(10) NOT NULL,
    density FLOAT,
    viscosity FLOAT,
    thermal_conductivity FLOAT,
    specific_heat FLOAT,
    reynolds FLOAT,
    prandtl FLOAT,
    FOREIGN KEY (heat_exchanger_id) REFERENCES heat_exchanger(id) ON DELETE CASCADE,
    UNIQUE KEY (heat_exchanger_id, timestamp, points, side)
) ENGINE=InnoDB;

-- 7. 创建性能参数表
CREATE TABLE performance_parameters (
    id INT PRIMARY KEY AUTO_INCREMENT,
    heat_exchanger_id INT NOT NULL,
    timestamp DATETIME NOT NULL,
    points INT NOT NULL,
    side VARCHAR(10) NOT NULL,
    K FLOAT,
    alpha_i FLOAT,
    alpha_o FLOAT,
    heat_duty FLOAT,
    effectiveness FLOAT,
    lmtd FLOAT,
    FOREIGN KEY (heat_exchanger_id) REFERENCES heat_exchanger(id) ON DELETE CASCADE,
    UNIQUE KEY (heat_exchanger_id, timestamp, points, side)
) ENGINE=InnoDB;

-- 8. 创建模型参数表
CREATE TABLE model_parameters (
    id INT PRIMARY KEY AUTO_INCREMENT,
    heat_exchanger_id INT NOT NULL,
    timestamp DATETIME NOT NULL,
    a FLOAT,
    p FLOAT,
    b FLOAT,
    FOREIGN KEY (heat_exchanger_id) REFERENCES heat_exchanger(id) ON DELETE CASCADE,
    UNIQUE KEY (heat_exchanger_id, timestamp)
) ENGINE=InnoDB;

-- 9. 创建K预测值表
CREATE TABLE k_predictions (
    id INT PRIMARY KEY AUTO_INCREMENT,
    heat_exchanger_id INT NOT NULL,
    timestamp DATETIME NOT NULL,
    points INT NOT NULL,
    side VARCHAR(10) NOT NULL,
    K_predicted FLOAT,
    FOREIGN KEY (heat_exchanger_id) REFERENCES heat_exchanger(id) ON DELETE CASCADE,
    UNIQUE KEY (heat_exchanger_id, timestamp, points, side)
) ENGINE=InnoDB;

-- 10. 插入初始数据
INSERT INTO heat_exchanger 
(id, type, tube_side_fluid, shell_side_fluid, tube_section_count, shell_section_count, d_i_original, d_o, lambda_t)
VALUES 
(1, '管壳式换热器', '水', '轻柴油', 30, 19, 0.02, 0.025, 45.0)
ON DUPLICATE KEY UPDATE 
type='管壳式换热器', 
tube_side_fluid='水', 
shell_side_fluid='轻柴油', 
tube_section_count=30, 
shell_section_count=19, 
d_i_original=0.02, 
d_o=0.025, 
lambda_t=45.0;

-- 11. 验证
SHOW DATABASES;
SHOW TABLES;
SELECT * FROM heat_exchanger;
