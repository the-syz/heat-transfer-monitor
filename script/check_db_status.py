#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os

# 添加backend目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))

from db.db_connection import DatabaseConnection

# 连接数据库
db = DatabaseConnection('../backend/config/config.json')
db.connect_test_db()
db.connect_prod_db()

# 检查模型参数
db.execute_query(db.prod_cursor, 'SELECT COUNT(*) as count FROM model_parameters WHERE day=1')
result = db.fetch_all(db.prod_cursor)
print(f'第1天模型参数数量: {result[0]["count"]}')

# 检查性能参数
db.execute_query(db.prod_cursor, 'SELECT COUNT(*) as count FROM performance_parameters WHERE day=10 AND hour=0')
result = db.fetch_all(db.prod_cursor)
print(f'第10天第0小时性能参数数量: {result[0]["count"]}')

# 检查所有天数
db.execute_query(db.prod_cursor, 'SELECT DISTINCT day FROM performance_parameters ORDER BY day')
result = db.fetch_all(db.prod_cursor)
days = [row['day'] for row in result]
print(f'性能参数表中的天数: {days}')

# 断开连接
db.disconnect_test_db()
db.disconnect_prod_db()