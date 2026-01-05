#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
检查model_parameters表中的训练参数
"""

import sys
import os

# 添加backend目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'backend')))

from db.db_connection import DatabaseConnection

def check_model_parameters():
    """检查model_parameters表中的训练参数"""
    # 初始化数据库连接
    config_path = os.path.join(os.path.dirname(__file__), 'backend', 'config', 'config.json')
    db_conn = DatabaseConnection(config_path)
    
    # 连接数据库
    db_conn.connect_prod_db()
    
    # 检查model_parameters表
    print("=== 检查生产数据库model_parameters表 ===")
    try:
        query = "SELECT * FROM heat_exchanger_monitor_db.model_parameters ORDER BY timestamp DESC LIMIT 5"
        if db_conn.execute_query(db_conn.prod_cursor, query):
            result = db_conn.fetch_all(db_conn.prod_cursor)
            if result:
                print(f"找到{len(result)}条记录：")
                for i, record in enumerate(result):
                    print(f"\n记录{i+1}:")
                    print(f"  ID: {record['id']}")
                    print(f"  时间戳: {record['timestamp']}")
                    print(f"  a: {record['a']}")
                    print(f"  p: {record['p']}")
                    print(f"  b: {record['b']}")
                    print(f"  heat_exchanger_id: {record['heat_exchanger_id']}")
            else:
                print("没有找到model_parameters数据")
    except Exception as e:
        print(f"查询model_parameters表失败: {e}")
    
    db_conn.disconnect_prod_db()

if __name__ == "__main__":
    check_model_parameters()
