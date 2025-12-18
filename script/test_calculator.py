import sys
import os
import json

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath('.'))
sys.path.insert(0, os.path.abspath('..'))

from backend.calculation.lmtd_calculator import LMTDCalculator
from backend.calculation.nonlinear_regression import NonlinearRegressionCalculator

def test_lmtd_calculator():
    """测试LMTD计算器"""
    print("测试LMTD计算器...")
    
    lmtd_calc = LMTDCalculator()
    
    # 测试LMTD计算
    lmtd = lmtd_calc.calculate_lmtd(80, 60, 20, 40, flow_type='counterflow')
    print(f"LMTD计算结果: {lmtd}")
    
    # 测试K_lmtd计算
    Q = 1000
    A = 1.0
    k_lmtd = lmtd_calc.calculate_k_lmtd(Q, A, lmtd)
    print(f"K_lmtd计算结果: {k_lmtd}")
    
    print("LMTD计算器测试完成\n")

def test_nonlinear_regression():
    """测试非线性回归计算器"""
    print("测试非线性回归计算器...")
    
    geometry_params = {
        'd_i_original': 0.02,
        'd_o': 0.025,
        'lambda_t': 45.0
    }
    
    nonlinear_calc = NonlinearRegressionCalculator(geometry_params)
    
    # 准备测试数据
    test_data = [
        {
            'reynolds_number': 10000,
            'K_lmtd': 500
        },
        {
            'reynolds_number': 20000,
            'K_lmtd': 600
        },
        {
            'reynolds_number': 30000,
            'K_lmtd': 650
        },
        {
            'reynolds_number': 40000,
            'K_lmtd': 700
        },
        {
            'reynolds_number': 50000,
            'K_lmtd': 750
        }
    ]
    
    # 测试模型训练
    a_opt, p_opt, b_opt = nonlinear_calc.get_optimized_parameters(test_data)
    model_params = {'a': a_opt, 'p': p_opt, 'b': b_opt}
    print(f"模型训练结果: {model_params}")
    
    # 测试K预测
    for record in test_data:
        K_pred = nonlinear_calc.predict_K(record['reynolds_number'], a_opt, p_opt, b_opt)
        print(f"Re={record['reynolds_number']}, K_lmtd={record['K_lmtd']}, K_pred={K_pred:.2f}")
    
    # 测试alpha_i计算
    alpha_i = nonlinear_calc.calculate_alpha_i(a_opt, p_opt, 10000)
    print(f"alpha_i计算结果: {alpha_i}")
    
    # 测试结垢热阻计算
    fouling_resistance = nonlinear_calc.calculate_fouling_resistance(30)
    print(f"第30天的结垢热阻: {fouling_resistance}")
    
    print("非线性回归计算器测试完成\n")

def test_model_func():
    """测试模型函数"""
    print("测试模型函数...")
    
    geometry_params = {
        'd_i_original': 0.02,
        'd_o': 0.025,
        'lambda_t': 45.0
    }
    
    nonlinear_calc = NonlinearRegressionCalculator(geometry_params)
    
    # 测试不同Re值下的模型输出
    Re_values = [5000, 10000, 20000, 30000, 40000, 50000]
    a = 1.0
    p = 0.8
    b = 0.0004
    
    for Re in Re_values:
        Y = nonlinear_calc.model_func(Re, a, p, b)
        K = 1 / Y if Y > 0 else 0
        print(f"Re={Re}, Y={Y:.6f}, K={K:.2f}")
    
    print("模型函数测试完成\n")

if __name__ == "__main__":
    print("开始测试后端计算程序...\n")
    
    test_lmtd_calculator()
    test_nonlinear_regression()
    test_model_func()
    
    print("所有测试完成！")
