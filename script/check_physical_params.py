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

# 检查测试数据库
print("=== 测试数据库检查 ===")
db.connect_test_db()

# 检查physical_parameters表是否存在
db.test_cursor.execute("SHOW TABLES LIKE 'physical_parameters'")
result = db.test_cursor.fetchone()
if result:
    print("✓ 测试数据库中存在physical_parameters表")
    
    # 查询记录数
    db.test_cursor.execute("SELECT COUNT(*) as count FROM physical_parameters")
    result = db.test_cursor.fetchone()
    print(f"  记录数: {result['count']}")
    
    if result['count'] > 0:
        # 查询最大时间
        db.test_cursor.execute("SELECT MAX(timestamp) as max_time, MIN(timestamp) as min_time FROM physical_parameters")
        result = db.test_cursor.fetchone()
        print(f"  时间范围: {result['min_time']} 至 {result['max_time']}")
        
        # 查询前5条记录
        db.test_cursor.execute("SELECT * FROM physical_parameters LIMIT 5")
        records = db.test_cursor.fetchall()
        print("  前5条记录:")
        for record in records:
            print(f"    {record}")
    else:
        print("  表为空")
else:
    print("✗ 测试数据库中不存在physical_parameters表")

db.disconnect_test_db()

# 检查生产数据库
print("\n=== 生产数据库检查 ===")
db.connect_prod_db()

# 查询physical_parameters表记录数
db.prod_cursor.execute("SELECT COUNT(*) as count FROM physical_parameters")
result = db.prod_cursor.fetchone()
print(f"生产数据库physical_parameters表记录数: {result['count']}")

if result['count'] > 0:
    # 查询最大时间
    db.prod_cursor.execute("SELECT MAX(timestamp) as max_time, MIN(timestamp) as min_time FROM physical_parameters")
    result = db.prod_cursor.fetchone()
    print(f"时间范围: {result['min_time']} 至 {result['max_time']}")
    
    # 查询前5条记录
    db.prod_cursor.execute("SELECT * FROM physical_parameters LIMIT 5")
    records = db.prod_cursor.fetchall()
    print("前5条记录:")
    for record in records:
        print(f"  {record}")

db.disconnect_prod_db()
