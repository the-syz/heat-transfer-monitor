import sys
import os
from datetime import datetime
import asyncio

# 添加项目根目录到Python路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from data.models import (
    HeatExchanger,
    OperationParameter,
    PhysicalParameter,
    PerformanceParameter,
    ModelParameter,
    KPrediction
)
from data.test_data.models import KPrediction as TestKPrediction

# 初始化数据库连接
async def init_db():
    from tortoise import Tortoise
    await Tortoise.init(
        db_url='mysql://heatexMCP:123123@localhost:3306/heat_exchanger_monitor_db',
        modules={'models': ['data.models', 'data.test_data.models']}
    )

# 关闭数据库连接
async def close_db():
    from tortoise import Tortoise
    await Tortoise.close_connections()

# 验证数据完整性
async def validate_data():
    """验证数据完整性"""
    print("=== 开始数据完整性测试 ===")
    print(f"当前时间: {datetime.now()}")
    
    # 测试结果
    test_results = {
        "total_tests": 0,
        "passed_tests": 0,
        "failed_tests": 0,
        "details": []
    }
    
    # 测试1: 验证换热器表是否有数据
    test_results["total_tests"] += 1
    he_count = await HeatExchanger.all().count()
    if he_count > 0:
        test_results["passed_tests"] += 1
        test_results["details"].append({"test": "换热器表数据检查", "status": "PASS", "message": f"换热器表有 {he_count} 条数据"})
    else:
        test_results["failed_tests"] += 1
        test_results["details"].append({"test": "换热器表数据检查", "status": "FAIL", "message": "换热器表没有数据"})
    
    # 测试2: 验证运行参数表数据
    test_results["total_tests"] += 1
    op_count = await OperationParameter.all().count()
    if op_count > 0:
        test_results["passed_tests"] += 1
        test_results["details"].append({"test": "运行参数表数据检查", "status": "PASS", "message": f"运行参数表有 {op_count} 条数据"})
    else:
        test_results["failed_tests"] += 1
        test_results["details"].append({"test": "运行参数表数据检查", "status": "FAIL", "message": "运行参数表没有数据"})
    
    # 测试3: 验证物性参数表数据
    test_results["total_tests"] += 1
    pp_count = await PhysicalParameter.all().count()
    if pp_count > 0:
        test_results["passed_tests"] += 1
        test_results["details"].append({"test": "物性参数表数据检查", "status": "PASS", "message": f"物性参数表有 {pp_count} 条数据"})
    else:
        test_results["failed_tests"] += 1
        test_results["details"].append({"test": "物性参数表数据检查", "status": "FAIL", "message": "物性参数表没有数据"})
    
    # 测试4: 验证性能参数表数据
    test_results["total_tests"] += 1
    perf_count = await PerformanceParameter.all().count()
    if perf_count > 0:
        test_results["passed_tests"] += 1
        test_results["details"].append({"test": "性能参数表数据检查", "status": "PASS", "message": f"性能参数表有 {perf_count} 条数据"})
    else:
        test_results["failed_tests"] += 1
        test_results["details"].append({"test": "性能参数表数据检查", "status": "FAIL", "message": "性能参数表没有数据"})
    
    # 测试5: 验证模型参数表数据
    test_results["total_tests"] += 1
    model_count = await ModelParameter.all().count()
    if model_count > 0:
        test_results["passed_tests"] += 1
        test_results["details"].append({"test": "模型参数表数据检查", "status": "PASS", "message": f"模型参数表有 {model_count} 条数据"})
    else:
        test_results["failed_tests"] += 1
        test_results["details"].append({"test": "模型参数表数据检查", "status": "FAIL", "message": "模型参数表没有数据"})
    
    # 测试6: 验证KPrediction表数据
    test_results["total_tests"] += 1
    k_pred_count = await KPrediction.all().count()
    if k_pred_count > 0:
        test_results["passed_tests"] += 1
        test_results["details"].append({"test": "KPrediction表数据检查", "status": "PASS", "message": f"KPrediction表有 {k_pred_count} 条数据"})
    else:
        test_results["failed_tests"] += 1
        test_results["details"].append({"test": "KPrediction表数据检查", "status": "FAIL", "message": "KPrediction表没有数据"})
    
    # 测试7: 验证operation_parameters表的points字段都是整数
    test_results["total_tests"] += 1
    # 查询所有不同的points值
    unique_points = await OperationParameter.all().distinct().values_list('points', flat=True)
    points_are_int = all(isinstance(p, int) for p in unique_points)
    if points_are_int:
        test_results["passed_tests"] += 1
        test_results["details"].append({"test": "运行参数表points字段类型检查", "status": "PASS", "message": "所有points值都是整数"})
    else:
        test_results["failed_tests"] += 1
        non_int_points = [p for p in unique_points if not isinstance(p, int)]
        test_results["details"].append({"test": "运行参数表points字段类型检查", "status": "FAIL", "message": f"发现非整数值: {non_int_points}"})
    
    # 测试8: 验证side字段只有tube和shell两种值
    test_results["total_tests"] += 1
    unique_sides = await OperationParameter.all().distinct().values_list('side', flat=True)
    valid_sides = {'tube', 'shell'}
    invalid_sides = set(unique_sides) - valid_sides
    if not invalid_sides:
        test_results["passed_tests"] += 1
        test_results["details"].append({"test": "side字段取值检查", "status": "PASS", "message": f"所有side值都是有效的: {unique_sides}"})
    else:
        test_results["failed_tests"] += 1
        test_results["details"].append({"test": "side字段取值检查", "status": "FAIL", "message": f"发现无效side值: {invalid_sides}"})
    
    # 测试9: 验证所有参数表都有heat_exchanger_id=1的数据
    test_results["total_tests"] += 1
    op_has_he1 = await OperationParameter.filter(heat_exchanger_id=1).count() > 0
    pp_has_he1 = await PhysicalParameter.filter(heat_exchanger_id=1).count() > 0
    perf_has_he1 = await PerformanceParameter.filter(heat_exchanger_id=1).count() > 0
    
    if op_has_he1 and pp_has_he1 and perf_has_he1:
        test_results["passed_tests"] += 1
        test_results["details"].append({"test": "外键heat_exchanger_id=1检查", "status": "PASS", "message": "所有参数表都有heat_exchanger_id=1的数据"})
    else:
        test_results["failed_tests"] += 1
        issues = []
        if not op_has_he1:
            issues.append("运行参数表")
        if not pp_has_he1:
            issues.append("物性参数表")
        if not perf_has_he1:
            issues.append("性能参数表")
        test_results["details"].append({"test": "外键heat_exchanger_id=1检查", "status": "FAIL", "message": f"以下表缺少heat_exchanger_id=1的数据: {', '.join(issues)}"})
    
    # 测试10: 验证performance_parameters表的K字段不为空
    test_results["total_tests"] += 1
    perf_without_k = await PerformanceParameter.filter(K__isnull=True).count()
    if perf_without_k == 0:
        test_results["passed_tests"] += 1
        test_results["details"].append({"test": "性能参数表K字段非空检查", "status": "PASS", "message": "所有性能参数记录都有K值"})
    else:
