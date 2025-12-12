-- 创建KManagement表的SQL脚本
-- 在测试数据库中执行

USE heat_exchanger_monitor_db;

-- 创建KManagement表
CREATE TABLE IF NOT EXISTS k_management (
    id INT PRIMARY KEY AUTO_INCREMENT,
    heat_exchanger_id INT NOT NULL,
    timestamp DATETIME NOT NULL,
    points INT NOT NULL,
    side VARCHAR(10) NOT NULL CHECK (side IN ('tube', 'shell')),
    K_LMTD FLOAT NULL COMMENT 'LMTD法计算的总传热系数 (W/(m²·K))',
    K_predicted FLOAT NULL COMMENT '预测总传热系数 (W/(m²·K))',
    K_actual FLOAT NULL COMMENT '实际总传热系数 (W/(m²·K))',
    FOREIGN KEY (heat_exchanger_id) REFERENCES heat_exchanger(id) ON DELETE CASCADE,
    UNIQUE KEY unique_k_management (heat_exchanger_id, timestamp, points, side)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='总传热系数管理表';

-- 查看表结构
DESCRIBE k_management;

-- 查看表创建语句
SHOW CREATE TABLE k_management;