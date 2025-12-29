#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查performance_parameters表的结构和数据
"""

import os
import sys
import json

# 添加backend目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))

try:
    from db.db_connection import DatabaseConnection
    
    # 读取配置文件
    backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend'))
    config_path = os.path.join(backend_dir, 'config', 'config.json')
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # 初始化数据库连接
    db_conn = DatabaseConnection(config)
    db_conn.connect_prod_db()
    
    print("=== performance_parameters表结构检查 ===")
    
    # 检查表是否存在
    check_table_sql = "SHOW TABLES LIKE 'performance_parameters'"
    if db_conn.execute_query(db_conn.prod_cursor, check_table_sql):
        result = db_conn.fetch_all(db_conn.prod_cursor)
        if len(result) > 0:
            print("✓ performance_parameters表存在")
            
            # 查看表结构
            print("\n表结构:")
            describe_sql = "DESCRIBE performance_parameters"
            if db_conn.execute_query(db_conn.prod_cursor, describe_sql):
                structure = db_conn.fetch_all(db_conn.prod_cursor)
                for field in structure:
                    print(f"  {field['Field']} ({field['Type']}) - {field.get('Null', 'NULL')}, {field.get('Key', '')}, {field.get('Default', '')}, {field.get('Extra', '')}")
            
            # 查看创建语句
            print("\n创建语句:")
            create_sql = "SHOW CREATE TABLE performance_parameters"
            if db_conn.execute_query(db_conn.prod_cursor, create_sql):
                create_stmt = db_conn.fetch_one(db_conn.prod_cursor)
                print(create_stmt['Create Table'])
            
            # 检查数据量
            count_sql = "SELECT COUNT(*) as total FROM performance_parameters"
            if db_conn.execute_query(db_conn.prod_cursor, count_sql):
                count_result = db_conn.fetch_one(db_conn.prod_cursor)
                print(f"\n数据总量: {count_result['total']}")
            
            # 检查前10条数据
            print("\n前10条数据:")
            select_sql = "SELECT * FROM performance_parameters LIMIT 10"
            if db_conn.execute_query(db_conn.prod_cursor, select_sql):
                sample_data = db_conn.fetch_all(db_conn.prod_cursor)
                for i, row in enumerate(sample_data):
                    print(f"\n记录 {i+1}:")
                    for key, value in row.items():
                        print(f"  {key}: {value}")
            
        else:
            print("✗ performance_parameters表不存在")
    
    db_conn.disconnect_prod_db()
    
except Exception as e:
    print(f"错误: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)