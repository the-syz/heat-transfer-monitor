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
    points_are_int = all