#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试Stage1完成回调函数
"""

import sys
import os
import json

# 添加backend目录到路径
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend'))
sys.path.insert(0, backend_dir)

from db.db_connection import DatabaseConnection
from calculation.main_calculator import MainCalculator

# 初始化数据库连接
config_file = os.path.join(backend_dir, 'config', 'config.json')
db = DatabaseConnection(config_file)

# 连接生产数据库
print("连接生产数据库...")
db.connect_prod_db()

# 查询第1天的性能数据
print("\n查询第1天的性能数据...")
sql = """SELECT COUNT(*) as count 
         FROM performance_parameters 
         WHERE timestamp BETWEEN '2022-01-01 00:00:00' AND '2022-01-01 23:59:59'"""
if db.execute_query(db.prod_cursor, sql):
    result = db.fetch_one(db.prod_cursor)
    print(f"第1天性能数据记录数: {result['count']}")
else:
    print("查询失败")

# 查询第1天第0小时的性能数据
print("\n查询第1天第0小时的性能数据...")
sql = """SELECT COUNT(*) as count 
         FROM performance_parameters 
         WHERE timestamp BETWEEN '2022-01-01 00:00:00' AND '2022-01-01 00:59:59'"""
if db.execute_query(db.prod_cursor, sql):
    result = db.fetch_one(db.prod_cursor)
    print(f"第1天第0小时性能数据记录数: {result['count']}")
else:
    print("查询失败")

# 查询第1天第0小时的前3条记录
print("\n查询第1天第0小时的前3条记录...")
sql = """SELECT id, timestamp, points, side, K, alpha_i, alpha_o, heat_duty 
         FROM performance_parameters 
         WHERE timestamp BETWEEN '2022-01-01 00:00:00' AND '2022-01-01 00:59:59'
         LIMIT 3"""
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

# 测试API调用
print("\n测试API调用...")
import requests

api_url = "http://localhost:8000/performance"
params = {"heat_exchanger_id": 1, "day": 1, "hour": 0}

try:
    response = requests.get(api_url, params=params, timeout=30)
    response.raise_for_status()
    data = response.json()
    print(f"API调用成功")
    print(f"状态: {data.get('status')}")
    print(f"记录数: {data.get('count')}")
    if data.get('data'):
        print(f"第一条记录: {data['data'][0]}")
    else:
        print("没有数据")
except Exception as e:
    print(f"API调用失败: {e}")
