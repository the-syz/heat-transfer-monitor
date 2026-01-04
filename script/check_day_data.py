#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os

# 添加backend目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))

from db.db_connection import DatabaseConnection

def check_day_data(day):
    """检查指定天数的performance_parameters数据"""
    backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend'))
    config_path = os.path.join(backend_dir, 'config', 'config.json')
    db = DatabaseConnection(config_path)
    try:
        db.connect_test_db()
        cursor = db.test_cursor
        
        # 查询测试数据库
        start_time = f"2022-01-{day:02d} 00:00:00"
        end_time = f"2022-01-{day:02d} 23:59:59"
        
        db.execute_query(cursor, 
            'SELECT COUNT(*) as count FROM performance_parameters WHERE timestamp BETWEEN %s AND %s', 
            (start_time, end_time))
        test_result = db.fetch_all(cursor)
        test_count = test_result[0]['count']
        
        # 查询生产数据库
        db.connect_prod_db()
        cursor = db.prod_cursor
        
        db.execute_query(cursor, 
            'SELECT COUNT(*) as count FROM performance_parameters WHERE timestamp BETWEEN %s AND %s', 
            (start_time, end_time))
        prod_result = db.fetch_all(cursor)
        prod_count = prod_result[0]['count']
        
        print(f"第{day}天数据统计:")
        print(f"  测试数据库performance_parameters记录数: {test_count}")
        print(f"  生产数据库performance_parameters记录数: {prod_count}")
        
        if test_count == 0:
            print(f"  ⚠️  测试数据库第{day}天没有数据！")
        if prod_count == 0:
            print(f"  ⚠️  生产数据库第{day}天没有数据！")
        
        return test_count, prod_count
        
    finally:
        db.disconnect_test_db()
        db.disconnect_prod_db()

if __name__ == "__main__":
    # 检查第10天的数据
    check_day_data(10)
    
    # 检查第1天的数据作为对比
    print("\n" + "="*50)
    check_day_data(1)
