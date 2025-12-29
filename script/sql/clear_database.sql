-- Active: 1757606878689@@127.0.0.1@3306@heat_exchanger_monitor_db
-- 清空heat_exchanger_monitor_db数据库中所有表的数据，但保留表结构

-- 设置外键检查为0，避免删除时的外键约束问题
SET FOREIGN_KEY_CHECKS = 0;

-- 清空各个表的数据，除去heat_exchanger表
TRUNCATE TABLE operation_parameters;
TRUNCATE TABLE physical_parameters;
TRUNCATE TABLE performance_parameters;
TRUNCATE TABLE k_management;
TRUNCATE TABLE model_parameters;

-- 恢复外键检查
SET FOREIGN_KEY_CHECKS = 1;

-- 显示清空结果
SELECT '数据库数据清空完成' AS result;
