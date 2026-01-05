#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
检查当前数据状态，看看是否有足够的数据触发Stage1训练
"""

import sys
import os

# 添加backend目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'backend')))

from db.db_connection import DatabaseConnection

def check_data_status():
    """检查当前数据状态"""
    # 初始化数据库连接
    config_path = os.path.join(os.path.dirname(__file__), 'backend', 'config', 'config.json')
    db_conn = DatabaseConnection(config_path)
    
    # 连接数据库
    db_conn.connect_test_db()
    db_conn.connect_prod_db()
    
    # 检查生产数据库physical_parameters表
    print("=== 检查生产数据库physical_parameters表 ===")
    try:
        query = """
        SELECT 
            MIN(day) as min_day,
            MAX(day) as max_day,
            COUNT(DISTINCT day) as total_days,
            COUNT(*) as total_records
        FROM (
            SELECT 
                DATE_FORMAT(timestamp, '%Y-%m-%d') as day
            FROM heat_exchanger_monitor_db.physical_parameters
        ) as days
        """
        if db_conn.execute_query(db_conn.prod_cursor, query):
            result = db_conn.fetch_all(db_conn.prod_cursor)
            if result:
                print(f"最小日期: {result[0]['min_day']}")
                print(f"最大日期: {result[0]['max_day']}")
                print(f"总天数: {result[0]['total_days']}")
                print(f"总记录数: {result[0]['total_records']}")
            else:
                print("没有找到physical_parameters数据")
    except Exception as e:
        print(f"查询physical_parameters表失败: {e}")
    
    # 检查生产数据库model_parameters表
    print("\n=== 检查生产数据库model_parameters表 ===")
    try:
        query = "SELECT COUNT(*) as count FROM heat_exchanger_monitor_db.model_parameters"
        if db_conn.execute_query(db_conn.prod_cursor, query):
            result = db_conn.fetch_all(db_conn.prod_cursor)
            if result:
                print(f"model_parameters表记录数: {result[0]['count']}")
            else:
                print("没有找到model_parameters数据")
    except Exception as e:
        print(f"查询model_parameters表失败: {e}")
    
    # 检查测试数据库operation_parameters表
    print("\n=== 检查测试数据库operation_parameters表 ===")
    try:
        query = """
        SELECT 
            MIN(day) as min_day,
            MAX(day) as max_day,
            COUNT(DISTINCT day) as total_days,
            COUNT(*) as total_records
        FROM (
            SELECT 
                DATE_FORMAT(timestamp, '%Y-%m-%d') as day
            FROM heat_exchanger_monitor_db_test.operation_parameters
        ) as days
        """
        if db_conn.execute_query(db_conn.test_cursor, query):
            result = db_conn.fetch_all(db_conn.test_cursor)
            if result:
                print(f"最小日期: {result[0]['min_day']}")
                print(f"最大日期: {result[0]['max_day']}")
                print(f"总天数: {result[0]['total_days']}")
                print(f"总记录数: {result[0]['total_records']}")
            else:
                print("没有找到operation_parameters数据")
    except Exception as e:
        print(f"查询operation_parameters表失败: {e}")
    
    # 检查测试数据库performance_parameters表
    print("\n=== 检查测试数据库performance_parameters表 ===")
    try:
        query = """
        SELECT 
            MIN(day) as min_day,
            MAX(day) as max_day,
            COUNT(DISTINCT day) as total_days,
            COUNT(*) as total_records
        FROM (
            SELECT 
                DATE_FORMAT(timestamp, '%Y-%m-%d') as day
            FROM heat_exchanger_monitor_db_test.performance_parameters
        ) as days
        """
        if db_conn.execute_query(db_conn.test_cursor, query):
            result = db_conn.fetch_all(db_conn.test_cursor)
            if result:
                print(f"最小日期: {result[0]['min_day']}")
                print(f"最大日期: {result[0]['max_day']}")
                print(f"总天数: {result[0]['total_days']}")
                print(f"总记录数: {result[0]['total_records']}")
            else:
                print("没有找到performance_parameters数据")
    except Exception as e:
        print(f"查询performance_parameters表失败: {e}")
    
    # 检查生产数据库k_management表
    print("\n=== 检查生产数据库k_management表 ===")
    try:
        query = """
        SELECT 
            COUNT(*) as total_records,
            COUNT(CASE WHEN K_predicted IS NOT NULL AND K_predicted > 0 THEN 1 END) as records_with_k_predicted
        FROM heat_exchanger_monitor_db.k_management
        """
        if db_conn.execute_query(db_conn.prod_cursor, query):
            result = db_conn.fetch_all(db_conn.prod_cursor)
            if result:
                print(f"k_management表总记录数: {result[0]['total_records']}")
                print(f"有K_predicted值的记录数: {result[0]['records_with_k_predicted']}")
            else:
                print("没有找到k_management数据")
    except Exception as e:
        print(f"查询k_management表失败: {e}")
    
    db_conn.disconnect_test_db()
    db_conn.disconnect_prod_db()

if __name__ == "__main__":
    check_data_status()


