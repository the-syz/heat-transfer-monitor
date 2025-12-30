#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试Stage1完成回调函数
"""

import sys
import os

# 添加backend目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'backend')))

from calculation.main_calculator import MainCalculator

def test_stage1_callback():
    """测试Stage1完成回调函数"""
    print("=== 测试Stage1完成回调函数 ===")
    
    # 初始化计算器
    config_path = os.path.join(os.path.dirname(__file__), 'backend', 'config', 'config.json')
    calculator = MainCalculator(config_path)
    
    # 设置回调函数
    def on_stage1_complete(day):
        print(f"\nStage1完成回调被触发！day={day}")
        print("开始输出结果文件...")
    
    calculator.set_stage1_complete_callback(on_stage1_complete)
    
    # 检查回调函数是否设置成功
    print(f"Stage1完成回调函数: {calculator.on_stage1_complete_callback}")
    
    # 检查当前状态
    print(f"当前stage: {calculator.stage}")
    print(f"当前model_params: {calculator.model_params}")
    print(f"training_days: {calculator.training_days}")
    
    # 尝试手动触发回调函数
    if calculator.on_stage1_complete_callback:
        print("\n手动触发Stage1完成回调函数...")
        calculator.on_stage1_complete_callback(20)
    else:
        print("\nStage1完成回调函数未设置！")

if __name__ == "__main__":
    test_stage1_callback()
