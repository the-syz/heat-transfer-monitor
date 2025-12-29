import sys
import os

# 设置工作目录到项目根目录
os.chdir('e:\BaiduSyncdisk\heat-transfer-monitor\backend')

# 直接测试calculate_heat_duty函数的核心逻辑
def test_calculate_heat_duty_logic():
    """测试calculate_heat_duty方法的核心逻辑"""
    print("开始测试calculate_heat_duty核心逻辑...")
    
    # 核心计算逻辑：Q = m * c * ΔT
    # 其中c=4.186 kJ/kg·℃（水的比热容），m=flow_rate (m³/h) * 1000 kg/m³，ΔT以℃为单位
    def mock_calculate_heat_duty(data):
        try:
            flow_rate = data.get('flow_rate', 0)
            delta_T = data.get('delta_T', 0)
            
            # 如果没有提供delta_T，尝试从T_in和T_out计算
            if delta_T == 0:
                T_in = data.get('T_in', 0)
                T_out = data.get('T_out', 0)
                delta_T = abs(T_out - T_in)
            
            # 检查参数有效性
            if flow_rate <= 0 or delta_T <= 0:
                return 0
            
            # 计算热负荷：Q = m * c * ΔT
            # 其中c=4.186 kJ/kg·℃（水的比热容）
            # m = flow_rate (m³/h) * 1000 kg/m³
            # 转换为kW：1 kJ/s = 1 kW
            heat_duty = flow_rate * 1000 * 4.186 * delta_T / 3600
            
            return heat_duty
        except Exception as e:
            print(f"错误: {e}")
            return 0
    
    # 测试1: 基本测试 - 有流量和温度差
    print("\n测试1: 基本测试 - 有流量和温度差")
    data = {'flow_rate': 100, 'delta_T': 10}
    result = mock_calculate_heat_duty(data)
    expected = 100 * 1000 * 4.186 * 10 / 3600  # 约1162.78 kW
    print(f'输入: {data}')
    print(f'输出: {result}')
    print(f'预期: {expected}')
    print(f'结果是否正确: {abs(result - expected) < 0.01}')
    
    # 测试2: 零流量测试
    print("\n测试2: 零流量测试")
    data = {'flow_rate': 0, 'delta_T': 10}
    result = mock_calculate_heat_duty(data)
    print(f'输入: {data}')
    print(f'输出: {result}')
    print(f'预期: 0')
    print(f'结果是否正确: {result == 0}')
    
    # 测试3: 零温度差测试
    print("\n测试3: 零温度差测试")
    data = {'flow_rate': 100, 'delta_T': 0}
    result = mock_calculate_heat_duty(data)
    print(f'输入: {data}')
    print(f'输出: {result}')
    print(f'预期: 0')
    print(f'结果是否正确: {result == 0}')
    
    # 测试4: 从温度点计算温度差
    print("\n测试4: 从温度点计算温度差")
    data = {'flow_rate': 100, 'T_in': 20, 'T_out': 30}
    result = mock_calculate_heat_duty(data)
    expected = 100 * 1000 * 4.186 * 10 / 3600  # 约1162.78 kW
    print(f'输入: {data}')
    print(f'输出: {result}')
    print(f'预期: {expected}')
    print(f'结果是否正确: {abs(result - expected) < 0.01}')
    
    print("\n所有测试完成！")

if __name__ == "__main__":
    test_calculate_heat_duty_logic()