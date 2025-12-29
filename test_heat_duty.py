import json
import sys
import os

# 添加backend目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

# 导入必要的模块
from calculation.main_calculator import MainCalculator

def test_calculate_heat_duty():
    """测试calculate_heat_duty方法"""
    print("开始测试calculate_heat_duty方法...")
    
    # 初始化计算器
    config_path = os.path.join(os.path.dirname(__file__), 'backend', 'config', 'config.json')
    calc = MainCalculator(config_path)
    
    # 测试1: 基本测试 - 有流量和温度差
    print("\n测试1: 基本测试 - 有流量和温度差")
    data = {'flow_rate': 100, 'delta_T': 10}
    result = calc.calculate_heat_duty(data)
    print(f'输入: {data}')
    print(f'输出: {result}')
    
    # 测试2: 零流量测试
    print("\n测试2: 零流量测试")
    data = {'flow_rate': 0, 'delta_T': 10}
    result = calc.calculate_heat_duty(data)
    print(f'输入: {data}')
    print(f'输出: {result}')
    
    # 测试3: 零温度差测试
    print("\n测试3: 零温度差测试")
    data = {'flow_rate': 100, 'delta_T': 0}
    result = calc.calculate_heat_duty(data)
    print(f'输入: {data}')
    print(f'输出: {result}')
    
    # 测试4: 从温度点计算温度差
    print("\n测试4: 从温度点计算温度差")
    data = {'flow_rate': 100, 'T_in': 20, 'T_out': 30}
    result = calc.calculate_heat_duty(data)
    print(f'输入: {data}')
    print(f'输出: {result}')
    
    print("\n所有测试完成！")

if __name__ == "__main__":
    test_calculate_heat_duty()