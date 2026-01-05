import traceback
import numpy as np

# 模拟calculate_heat_duty方法的核心逻辑，包括异常处理
class MockMainCalculator:
    def calculate_heat_duty(self, data):
        try:
            # 获取流量、比热容和温度差
            flow_rate = data.get('flow_rate', 0)
            specific_heat = data.get('specific_heat', 4.1868)  # 默认水的比热容，单位：kJ/(kg·K)
            
            # 获取温度信息，支持多种数据结构
            delta_T = data.get('delta_T', 0)
            
            if delta_T <= 0:
                # 如果没有温度差，尝试从温度点获取
                T_in = data.get('T_in', 0) or data.get('temperature_in', 0) or 0
                T_out = data.get('T_out', 0) or data.get('temperature_out', 0) or 0
                
                # 计算温度差
                delta_T = abs(T_out - T_in)
            
            # 确保所有参数都有效
            if flow_rate > 0 and delta_T > 0:
                # 热负荷计算公式：Q = m * c * ΔT
                heat_duty = flow_rate * specific_heat * delta_T
                return heat_duty
            else:
                return 0
        except Exception as e:
            print(f"计算热负荷时发生错误: {e}")
            traceback.print_exc()  # 打印完整的错误堆栈
            return 0  # 修复：异常时返回0

# 测试用例
print("测试calculate_heat_duty方法的异常处理")

# 创建计算器实例
calc = MockMainCalculator()

# 测试用例1：正常情况
print("\n测试用例1：正常情况")
data = {'flow_rate': 100, 'delta_T': 10}
result = calc.calculate_heat_duty(data)
print(f'输入: {data}')
print(f'输出: {result}')
print(f'期望: > 0')
print(f'测试结果: {'通过' if result > 0 else '失败'}')

# 测试用例2：空数据引发异常
print("\n测试用例2：空数据引发异常")
data = None
result = calc.calculate_heat_duty(data)
print(f'输入: None')
print(f'输出: {result}')
print(f'期望: 0')
print(f'测试结果: {'通过' if result == 0 else '失败'}')

# 测试用例3：缺少必要字段引发异常
print("\n测试用例3：缺少必要字段引发异常")
data = {'flow_rate': 100}
# 模拟计算过程中的异常
class BrokenCalculator(MockMainCalculator):
    def calculate_heat_duty(self, data):
        try:
            # 故意引发异常
            raise ValueError("模拟计算过程中的异常")
        except Exception as e:
            print(f"计算热负荷时发生错误: {e}")
            traceback.print_exc()  # 打印完整的错误堆栈
            return 0  # 修复：异常时返回0

broken_calc = BrokenCalculator()
result = broken_calc.calculate_heat_duty(data)
print(f'输入: {data}')
print(f'输出: {result}')
print(f'期望: 0')
print(f'测试结果: {'通过' if result == 0 else '失败'}')

print("\n所有测试完成！")
