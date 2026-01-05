import sys
import os
import numpy as np

# 确保当前目录是backend
exe_path = os.path.abspath(__file__)
base_dir = os.path.dirname(exe_path)
os.chdir(base_dir)

# 导入MainCalculator类
try:
    # 从当前目录导入MainCalculator
    from calculation.main_calculator import MainCalculator
    print("成功导入MainCalculator类")
    
    # 创建MainCalculator实例
    calc = MainCalculator('config/config.json')
    print("成功创建MainCalculator实例")
    
    # 测试用例1：基本测试
    print("\n测试用例1：基本测试")
    data = {'flow_rate': 100, 'delta_T': 10}
    result = calc.calculate_heat_duty(data)
    print(f'输入: {data}')
    print(f'输出: {result}')
    assert result > 0, "基本测试失败"
    
    # 测试用例2：零流量测试
    print("\n测试用例2：零流量测试")
    data = {'flow_rate': 0, 'delta_T': 10}
    result = calc.calculate_heat_duty(data)
    print(f'输入: {data}')
    print(f'输出: {result}')
    assert result == 0, "零流量测试失败"
    
    # 测试用例3：零温度差测试
    print("\n测试用例3：零温度差测试")
    data = {'flow_rate': 100, 'delta_T': 0}
    result = calc.calculate_heat_duty(data)
    print(f'输入: {data}')
    print(f'输出: {result}')
    assert result == 0, "零温度差测试失败"
    
    # 测试用例4：从温度点计算温度差
    print("\n测试用例4：从温度点计算温度差")
    data = {'flow_rate': 100, 'T_in': 20, 'T_out': 30}
    result = calc.calculate_heat_duty(data)
    print(f'输入: {data}')
    print(f'输出: {result}')
    assert result > 0, "从温度点计算温度差测试失败"
    
    print("\n所有测试用例通过！")
    
except Exception as e:
    print(f"测试过程中发生错误: {e}")
    import traceback
    traceback.print_exc()
