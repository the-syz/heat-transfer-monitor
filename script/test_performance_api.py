#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试性能API端点，查看返回数据情况
"""

import os
import sys
import json
import requests

# 添加backend目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))

try:
    from db.db_connection import DatabaseConnection
    
    # 读取配置文件
    backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend'))
    config_path = os.path.join(backend_dir, 'config', 'config.json')
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # 测试API直接查询
    print("=== 测试API直接查询 ===")
    
    # 测试API的performance端点
    api_url = "http://localhost:8000"
    endpoint = "/performance"
    
    # 测试第1天第0小时
    params = {
        "heat_exchanger_id": 1,
        "day": 1,
        "hour": 0
    }
    
    try:
        response = requests.get(f"{api_url}{endpoint}", params=params)
        response.raise_for_status()
        data = response.json()
        
        print(f"API查询结果状态: {data.get('status')}")
        print(f"返回数据量: {data.get('count', 0)}")
        
        if data.get('data'):
            print("\n前3条数据:")
            for i, record in enumerate(data['data'][:3]):
                print(f"\n记录 {i+1}:")
                for key, value in record.items():
                    print(f"  {key}: {value}")
        else:
            print("\n没有返回数据")
            
            # 尝试直接查询数据库的performance_parameters表
            print("\n=== 直接查询performance_parameters表 ===")
            db_conn = DatabaseConnection(config)
            db_conn.connect_prod_db()
            
            sql = "SELECT * FROM performance_parameters WHERE heat_exchanger_id = %s AND timestamp BETWEEN %s AND %s"
            start_time = f"2022-01-{params['day']:02d} {params['hour']:02d}:00:00"
            end_time = f"2022-01-{params['day']:02d} {params['hour']:02d}:59:59"
            
            if db_conn.execute_query(db_conn.prod_cursor, sql, [params['heat_exchanger_id'], start_time, end_time]):
                results = db_conn.fetch_all(db_conn.prod_cursor)
                print(f"直接查询结果数量: {len(results)}")
                
                if results:
                    print("\n直接查询到的数据:")
                    for i, record in enumerate(results[:3]):
                        print(f"\n记录 {i+1}:")
                        for key, value in record.items():
                            print(f"  {key}: {value}")
            
            db_conn.disconnect_prod_db()
    
    except requests.exceptions.RequestException as e:
        print(f"API调用失败: {e}")
        
        # 尝试直接查询数据库
        print("\n=== 直接查询performance_parameters表 ===")
        db_conn = DatabaseConnection(config)
        db_conn.connect_prod_db()
        
        sql = "SELECT * FROM performance_parameters WHERE heat_exchanger_id = %s AND timestamp BETWEEN %s AND %s"
        start_time = f"2022-01-{params['day']:02d} {params['hour']:02d}:00:00"
        end_time = f"2022-01-{params['day']:02d} {params['hour']:02d}:59:59"
        
        if db_conn.execute_query(db_conn.prod_cursor, sql, [params['heat_exchanger_id'], start_time, end_time]):
            results = db_conn.fetch_all(db_conn.prod_cursor)
            print(f"直接查询结果数量: {len(results)}")
            
            if results:
                print("\n直接查询到的数据:")
                for i, record in enumerate(results[:3]):
                    print(f"\n记录 {i+1}:")
                    for key, value in record.items():
                        print(f"  {key}: {value}")
        
        db_conn.disconnect_prod_db()
    
    # 测试k_management表的数据
    print("\n=== 测试k_management表数据 ===")
    db_conn = DatabaseConnection(config)
    db_conn.connect_prod_db()
    
    sql = "SELECT * FROM k_management WHERE heat_exchanger_id = %s AND timestamp BETWEEN %s AND %s"
    start_time = f"2022-01-{params['day']:02d} {params['hour']:02d}:00:00"
    end_time = f"2022-01-{params['day']:02d} {params['hour']:02d}:59:59"
    
    if db_conn.execute_query(db_conn.prod_cursor, sql, [params['heat_exchanger_id'], start_time, end_time]):
        results = db_conn.fetch_all(db_conn.prod_cursor)
        print(f"k_management表查询结果数量: {len(results)}")
        
        if results:
            print("\nk_management表数据:")
            for i, record in enumerate(results[:3]):
                print(f"\n记录 {i+1}:")
                for key, value in record.items():
                    print(f"  {key}: {value}")
    
    db_conn.disconnect_prod_db()
    
except Exception as e:
    print(f"错误: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)