#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证修复的功能模块
"""

import os
import sys
import json
import logging

# 添加backend目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../backend')))

try:
    from calculation.main_calculator import MainCalculator
    from db.db_connection import DatabaseConnection
    
    # 设置日志
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger('validate_fixes')
    
    print("=== 验证修复的功能模块 ===")
    
    # 1. 验证calculate_heat_duty方法修复
    print("\n1. 验证calculate_heat_duty方法修复")
    
    # 读取配置文件
    backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../backend'))
    config_path = os.path.join(backend_dir, 'config', 'config.json')
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # 初始化计算器
    calculator = MainCalculator(config_path)
    
    # 测试calculate_heat_duty方法
    try:
        # 测试正常情况
        data = {
            'flow_rate': 100.0,  # kg/h
            'specific_heat': 4.186,  # kJ/(kg·K)
            'T_in': 80.0,  # °C
            'T_out': 60.0,  # °C
            'side': 'tube',
            'timestamp': '2022-01-01 00:00:00'
        }
        
        result = calculator.calculate_heat_duty(data)
        expected = data['flow_rate'] * data['specific_heat'] * abs(data['T_in'] - data['T_out'])
        
        print(f"  正常情况测试: {result} (预期: {expected})")
        if abs(result - expected) < 0.0001:
            print("  ✓ 正常情况测试通过")
        else:
            print("  ✗ 正常情况测试失败")
        
        # 测试异常情况（流量为0）
        data_flow_zero = data.copy()
        data_flow_zero['flow_rate'] = 0.0
        
        result = calculator.calculate_heat_duty(data_flow_zero)
        print(f"  异常情况测试（流量为0）: {result}")
        if result == 0:
            print("  ✓ 异常情况测试通过")
        else:
            print("  ✗ 异常情况测试失败")
            
        # 测试异常情况（温差为0）
        data_temp_zero = data.copy()
        data_temp_zero['T_out'] = data_temp_zero['T_in']
        
        result = calculator.calculate_heat_duty(data_temp_zero)
        print(f"  异常情况测试（温差为0）: {result}")
        if result == 0:
            print("  ✓ 异常情况测试通过")
        else:
            print("  ✗ 异常情况测试失败")
            
    except Exception as e:
        print(f"  ✗ calculate_heat_duty方法测试异常: {e}")
        import traceback
        traceback.print_exc()
    
    # 2. 验证K_LMTD字段名修复
    print("\n2. 验证K_LMTD字段名修复")
    
    try:
        # 查询k_management表
        db_conn = DatabaseConnection(config)
        db_conn.connect_prod_db()
        
        # 查询是否有K_LMTD字段的值
        sql = "SELECT COUNT(*) as total, COUNT(K_LMTD) as lmtd_count FROM k_management WHERE heat_exchanger_id = 1 LIMIT 100"
        if db_conn.execute_query(db_conn.prod_cursor, sql):
            result = db_conn.fetch_one(db_conn.prod_cursor)
            print(f"  k_management表K_LMTD字段统计:")
            print(f"  总记录数: {result['total']}")
            print(f"  K_LMTD有值记录数: {result['lmtd_count']}")
            
            if result['lmtd_count'] > 0:
                print("  ✓ K_LMTD字段有值，修复成功")
            else:
                print("  ✗ K_LMTD字段无值，需要检查数据插入逻辑")
            
            # 查看示例数据
            sql = "SELECT * FROM k_management WHERE heat_exchanger_id = 1 AND K_LMTD IS NOT NULL LIMIT 5"
            if db_conn.execute_query(db_conn.prod_cursor, sql):
                sample_data = db_conn.fetch_all(db_conn.prod_cursor)
                if sample_data:
                    print("  示例数据:")
                    for i, record in enumerate(sample_data[:3]):
                        print(f"    记录 {i+1}: K_LMTD = {record['K_LMTD']}, K_predicted = {record['K_predicted']}")
        
        db_conn.disconnect_prod_db()
        
    except Exception as e:
        print(f"  ✗ K_LMTD字段验证异常: {e}")
        import traceback
        traceback.print_exc()
    
    # 3. 验证API查询功能
    print("\n3. 验证API查询功能")
    
    try:
        import requests
        
        # 测试performance API
        api_url = "http://localhost:8000"
        endpoint = "/performance"
        params = {
            "heat_exchanger_id": 1,
            "day": 1,
            "hour": 0
        }
        
        response = requests.get(f"{api_url}{endpoint}", params=params)
        response.raise_for_status()
        data = response.json()
        
        print(f"  API查询状态: {data.get('status')}")
        print(f"  返回数据量: {data.get('count', 0)}")
        
        if data.get('status') == 'success' and data.get('count', 0) > 0:
            print("  ✓ API查询功能正常")
        else:
            print("  ✗ API查询功能异常")
            
    except requests.exceptions.RequestException as e:
        print(f"  ✗ API测试异常: {e}")
    except Exception as e:
        print(f"  ✗ API测试异常: {e}")
    
    print("\n=== 验证完成 ===")
    
except Exception as e:
    print(f"验证脚本异常: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)