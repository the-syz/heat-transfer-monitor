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

# 检查physical_parameters表结构
print("=== physical_parameters表结构 ===")
db.prod_cursor.execute('DESCRIBE physical_parameters')
result = db.prod_cursor.fetchall()
for row in result:
    print(f"  {row['Field']}: {row['Type']} {'(主键)' if row['Key'] == 'PRI' else ''}")

print("\n=== k_management表结构 ===")
db.prod_cursor.execute('DESCRIBE k_management')
result = db.prod_cursor.fetchall()
for row in result:
    print(f"  {row['Field']}: {row['Type']} {'(主键)' if row['Key'] == 'PRI' else ''}")

print("\n=== model_parameters表结构 ===")
db.prod_cursor.execute('DESCRIBE model_parameters')
result = db.prod_cursor.fetchall()
for row in result:
    print(f"  {row['Field']}: {row['Type']} {'(主键)' if row['Key'] == 'PRI' else ''}")
