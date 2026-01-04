#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
检查performance_parameters表的数据
"""

import sys
import os

# 添加backend目录到路径
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend'))
sys.path.insert(0, backend_dir)

from db.db_connection import DatabaseConnection

# 初始化数据库连接
config_file = os.path.join(backend_dir, 'config', 'config.json')
db = DatabaseConnection(config_file)

# 连接生产数据库
print("连接生产数据库...")
db.connect_prod_db()

# 查询performance_parameters表的总记录数
print("\n查询performance_parameters表的总记录数...")
sql = "SELECT COUNT(*) as total FROM performance_parameters"
if db.execute_query(db.prod_cursor, sql):
    result = db.fetch_one(db.prod_cursor)
    print(f"总记录数: {result['total']}")
else:
    print("查询失败")

# 查询第1天的记录数
print("\n查询第1天的记录数...")
sql = "SELECT COUNT(*) as count FROM performance_parameters WHERE timestamp BETWEEN '2022-01-01 00:00:00' AND '2022-01-01 23:59:59'"
if db.execute_query(db.prod_cursor, sql):
    result = db.fetch_one(db.prod_cursor)
    print(f"第1天记录数: {result['count']}")
else:
    print("查询失败")

# 查询第10天第0小时的记录数
print("\n查询第10天第0小时的记录数...")
sql = "SELECT COUNT(*) as count FROM performance_parameters WHERE timestamp BETWEEN '2022-01-10 00:00:00' AND '2022-01-10 00:59:59'"
if db.execute_query(db.prod_cursor, sql):
    result = db.fetch_one(db.prod_cursor)
    print(f"第10天第0小时记录数: {result['count']}")
else:
    print("查询失败")

# 查询第10天第0小时的前5条记录
print("\n查询第10天第0小时的前5条记录...")
sql = """SELECT id, timestamp, points, side, K, alpha_i, alpha_o, heat_duty 
         FROM performance_parameters 
         WHERE timestamp BETWEEN '2022-01-10 00:00:00' AND '2022-01-10 00:59:59'
         LIMIT 5"""
if db.execute_query(db.prod_cursor, sql):
    results = db.fetch_all(db.prod_cursor)
    print(f"找到 {len(results)} 条记录:")
    for row in results:
        print(f"  ID: {row['id']}, 时间: {row['timestamp']}, Points: {row['points']}, Side: {row['side']}, K: {row['K']}")
else:
    print("查询失败")

# 断开连接
db.disconnect_prod_db()
print("\n数据库连接已关闭")

