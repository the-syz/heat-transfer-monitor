#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.insert(0, 'backend')

from calculation.main_calculator import MainCalculator
import json

# 加载配置
config = json.load(open('backend/config/config.json'))

# 初始化MainCalculator
calculator = MainCalculator('backend/config/config.json')

# 测试处理第20天第23小时的数据（应该触发stage1训练）
print("=== 测试处理第20天第23小时的数据 ===")
print(f"当前stage: {calculator.stage}")
print(f"当前model_params: {calculator.model_params}")
print(f"training_days: {calculator.training_days}")

# 调用process_data_by_hour
result = calculator.process_data_by_hour(20, 23)
print(f"\n处理结果: {result}")

# 检查生产数据库中的model_parameters表
print("\n=== 检查生产数据库model_parameters表 ===")
calculator.data_loader.db_conn.connect_prod_db()
calculator.data_loader.db_conn.prod_cursor.execute("SELECT COUNT(*) as count FROM model_parameters")
result = calculator.data_loader.db_conn.prod_cursor.fetchone()
print(f"记录数: {result['count']}")

if result['count'] > 0:
    calculator.data_loader.db_conn.prod_cursor.execute("SELECT * FROM model_parameters ORDER BY timestamp DESC LIMIT 5")
    records = calculator.data_loader.db_conn.prod_cursor.fetchall()
    print("最近5条记录:")
    for record in records:
        print(f"  {record}")

calculator.data_loader.db_conn.disconnect_prod_db()
