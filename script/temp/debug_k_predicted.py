#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
调试K_predicted为None的问题
"""
import sys
import os
import numpy as np

# 添加项目根目录到Python路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from backend.calculation.main_calculator import MainCalculator
from backend.calculation.nonlinear_regression import NonlinearRegressionCalculator
from backend.db.data_loader import DataLoader
from backend.db.db_connection import DatabaseConnection


def debug_k_predicted():
    """调试K_predicted为None的问题"""
    print("=== 调试K_predicted为None的问题 ===")
    
    # 创建数据库连接
    db_conn = DatabaseConnection()
    if not db_conn.connect_to_test_db():
        print("连接测试数据库失败")
        return
    if not db_conn.connect_to_prod_db():
        print("连接生产数据库失败")
        return
    
    # 创建数据加载器
    data_loader = DataLoader(db_conn)
    
    # 获取换热器信息
    heat_exchanger_info = data_loader.get_heat_exchanger_info(1)
    if not heat_exchanger_info:
        print("获取换热器信息失败")
        return
    
    print(f"换热器信息: {heat_exchanger_info}")
    
    # 创建非线性回归计算器
    nonlinear_calc = NonlinearRegressionCalculator(heat_exchanger_info)
    
    # 创建主计算器
    main_calc = MainCalculator(data_loader, nonlinear_calc, heat_exchanger_info)
    
    # 阶段1训练
    print("\n=== 阶段1训练 ===")
    model_params = main_calc.train_stage1()
    print(f"阶段1训练结果: {model_params}")
    print(f"model_params属性: {main_calc.model_params}")
    
    # 处理一天一小时的数据
    print("\n=== 处理测试数据 ===")
    day = 1
    hour = 0
    
    # 测试predict_k_and_alpha_i方法
    print("\n=== 测试predict_k_and_alpha_i方法 ===")
    
    # 获取运行参数数据
    operation_data = data_loader.get_operation_parameters_by_hour(day, hour)
    print(f"运行参数数据量: {len(operation_data)}")
    if operation_data:
        print(f"运行参数示例: {operation_data[0]}")
    
    # 计算物理参数
    physical_data = data_loader.get_physical_parameters_by_hour(day, hour)
    processed_data = data_loader.process_operation_data(operation_data, physical_data, heat_exchanger_info)
    print(f"处理后的数据量: {len(processed_data)}")
    if processed_data:
        print(f"处理后的数据示例: {processed_data[0]}")
    
    # 过滤tube侧数据
    tube_processed_data = [data for data in processed_data if data.get('side', '').lower() == 'tube']
    print(f"Tube侧数据量: {len(tube_processed_data)}")
    if tube_processed_data:
        print(f"Tube侧数据示例: {tube_processed_data[0]}")
        print(f"Reynolds值: {tube_processed_data[0].get('reynolds', '未找到')}")
    
    # 测试预测K值
    if main_calc.model_params:
        k_predicted_map, alpha_i_map = main_calc.predict_k_and_alpha_i(tube_processed_data)
        print(f"预测的K值映射表大小: {len(k_predicted_map)}")
        if k_predicted_map:
            print(f"K值映射表示例: {list(k_predicted_map.items())[:1]}")
        else:
            print("K值映射表为空")
            # 进一步调试
            print("\n=== 调试预测为空的原因 ===")
            for data in tube_processed_data:
                Re = data.get('reynolds', 0)
                print(f"Reynolds值: {Re}, 是否>0: {Re > 0}")
                if Re > 0 and main_calc.model_params:
                    K_pred = main_calc.nonlinear_calc.predict_K(Re, main_calc.model_params['a'], main_calc.model_params['p'], main_calc.model_params['b'])
                    print(f"直接调用predict_K结果: {K_pred}")
    else:
        print("model_params为空，无法预测K值")
    
    # 测试process_data_by_hour方法
    print("\n=== 测试process_data_by_hour方法 ===")
    success = main_calc.process_data_by_hour(day, hour)
    print(f"处理数据结果: {success}")
    
    # 验证数据库中的K_predicted值
    print("\n=== 验证数据库中的K_predicted值 ===")
    # 读取k_management表的前几条记录
    query = "SELECT * FROM k_management WHERE K_predicted IS NOT NULL LIMIT 5"
    db_conn.prod_cursor.execute(query)
    results = db_conn.prod_cursor.fetchall()
    print(f"找到 {len(results)} 条记录")
    for row in results:
        print(f"记录: {row}")
        print(f"K_predicted: {row[4]}")  # 假设第5列是K_predicted
    
    # 关闭数据库连接
    db_conn.close_connection()
    
    print("\n=== 调试完成 ===")


if __name__ == "__main__":
    debug_k_predicted()