#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.insert(0, 'backend')

from db.db_connection import DatabaseConnection
import json

# 加载配置
config = json.load(open('backend/config/config.json'))
db = DatabaseConnection(config)
db.connect_prod_db()

# 检查各表的数据情况
print("=== 数据库状态检查 ===")

# operation_parameters表
db.prod_cursor.execute('SELECT MAX(DAY(timestamp)) as max_day, MAX(HOUR(timestamp)) as max_hour, COUNT(*) as count FROM operation_parameters')
result = db.prod_cursor.fetchone()
if result:
    print(f"operation_parameters表: 最大天数={result['max_day']}, 最大小时={result['max_hour']}, 总记录数={result['count']}")
else:
    print("operation_parameters表: 无数据")

# physical_parameters表
db.prod_cursor.execute('SELECT MAX(DAY(timestamp)) as max_day, MAX(HOUR(timestamp)) as max_hour, COUNT(*) as count FROM physical_parameters')
result = db.prod_cursor.fetchone()
if result:
    print(f"physical_parameters表: 最大天数={result['max_day']}, 最大小时={result['max_hour']}, 总记录数={result['count']}")
else:
    print("physical_parameters表: 无数据")

# k_management表
db.prod_cursor.execute('SELECT MAX(DAY(timestamp)) as max_day, MAX(HOUR(timestamp)) as max_hour, COUNT(*) as count FROM k_management')
result = db.prod_cursor.fetchone()
if result:
    print(f"k_management表: 最大天数={result['max_day']}, 最大小时={result['max_hour']}, 总记录数={result['count']}")
else:
    print("k_management表: 无数据")

# model_parameters表
db.prod_cursor.execute('SELECT COUNT(*) as count FROM model_parameters')
result = db.prod_cursor.fetchone()
if result:
    print(f"model_parameters表: 记录数={result['count']}")
    if result['count'] > 0:
        db.prod_cursor.execute('SELECT * FROM model_parameters ORDER BY timestamp DESC LIMIT 5')
        results = db.prod_cursor.fetchall()
        print("最近的5条model_parameters记录:")
        for row in results:
            print(f"  {row}")
else:
    print("model_parameters表: 无数据")

# 检查配置
print("\n=== 配置信息 ===")
backend_config = json.load(open('backend/config/config.json'))
print(f"training_days: {backend_config.get('training_days', 20)}")
print(f"optimization_hours: {backend_config.get('optimization_hours', 3)}")
print(f"stage1_error_threshold: {backend_config.get('stage1_error_threshold', 5)}")


