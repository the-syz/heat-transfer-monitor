import sys
import os
from datetime import datetime
import asyncio
import pandas as pd

# 添加项目根目录到Python路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from data.test_data.models import (
    OperationParameter,
    PhysicalParameter,
    PerformanceParameter,
    ModelParameter,
    KPrediction
)
from utils import (
    init_db,
    close_db,
    process_points,
    convert_to_timestamp,
    read_csv_file,
    batch_insert,
    get_all_csv_files,
    get_day_from_filename
)
from config import DATA_SOURCE_PATHS, IMPORT_CONFIG

# 导入cache/day_X_full_data.csv文件
async def import_cache_full_data(file_path):
    """导入cache/day_X_full_data.csv文件数据
    
    Args:
        file_path (str): 文件路径
        
    Returns:
        dict: 导入结果统计
    """
    print(f"开始导入文件: {file_path}")
    
    # 读取CSV文件
    df = read_csv_file(file_path)
    if df is None:
        return {"file": file_path, "success": False, "message": "读取文件失败"}
    
    # 从文件名获取day
    day = get_day_from_filename(file_path)
    if day is None:
        # 尝试从数据中获取day
        if 'day' in df.columns:
            day = df['day'].iloc[0] if not df.empty else 0
        else:
            day = 0
    
    # 初始化数据列表
    operation_data = []
    physical_data = []
    performance_data = []
    k_prediction_data = []
    
    # 处理每行数据
    for _, row in df.iterrows():
        # 处理points和side
        points_str = row.get('points', '')
        points, side = process_points(str(points_str))
        if points is None:
            continue
        
        # 获取hour
        hour = row.get('hour', 0)
        if isinstance(hour, str):
            try:
                hour = float(hour)
            except ValueError:
                hour = 0
        hour = int(hour)
        
        # 转换为时间戳
        timestamp = convert_to_timestamp(day, hour)
        
        # 换热器编号，默认为1
        heat_exchanger_id = 1
        
        # 1. 运行参数数据
        operation_param = OperationParameter(
            heat_exchanger_id=heat_exchanger_id,
            timestamp=timestamp,
            points=points,
            side=side,
            temperature=row.get('temperature'),
            pressure=row.get('pressure'),  # 如果没有pressure字段，会使用默认值None
            flow_rate=row.get('flow_rate'),  # 如果没有flow_rate字段，会使用默认值None
            velocity=row.get('u')  # u字段对应velocity
        )
        operation_data.append(operation_param)
        
        # 2. 物性参数数据
        physical_param = PhysicalParameter(
            heat_exchanger_id=heat_exchanger_id,
            timestamp=timestamp,
            points=points,
            side=side,
            density=row.get('rho'),
            viscosity=row.get('mu'),
            thermal_conductivity=row.get('lambda'),
            specific_heat=row.get('Cp'),
            reynolds=row.get('Re'),
            prandtl=row.get('Pr')
        )
        physical_data.append(physical_param)
        
        # 3. 性能参数数据
        # K值可以来自K或K_actual字段
        k_value = row.get('K')
        if pd.isna(k_value):
            k_value = row.get('K_actual')
        
        performance_param = PerformanceParameter(
            heat_exchanger_id=heat_exchanger_id,
            timestamp=timestamp,
            points=points,
            side=side,
            K=k_value,
            alpha_i=row.get('alpha_i'),
            alpha_o=row.get('alpha_o'),
            heat_duty=row.get('heat_duty'),  # 如果没有这些字段，会使用默认值None
            effectiveness=row.get('effectiveness'),
            lmtd=row.get('LMTD')
        )
        performance_data.append(performance_param)
        
        # 4. K_predicted数据
        k_predicted = row.get('K_predicted')
        if not pd.isna(k_predicted):
            k_pred_data = KPrediction(
                heat_exchanger_id=heat_exchanger_id,
                timestamp=timestamp,
                points=points,
                side=side,
                K_predicted=k_predicted
            )
            k_prediction_data.append(k_pred_data)
    
    # 批量插入数据
    inserted_counts = {}
    
    if operation_data:
        inserted_counts['operation_parameters'] = await batch_insert(OperationParameter, operation_data, IMPORT_CONFIG['batch_size'])
    
    if physical_data:
        inserted_counts['physical_parameters'] = await batch_insert(PhysicalParameter, physical_data, IMPORT_CONFIG['batch_size'])
    
    if performance_data:
        inserted_counts['performance_parameters'] = await batch_insert(PerformanceParameter, performance_data, IMPORT_CONFIG['batch_size'])
    
    if k_prediction_data:
        inserted_counts['k_predictions'] = await batch_insert(KPrediction, k_prediction_data, IMPORT_CONFIG['batch_size'])
    
    print(f"文件 {file_path} 导入完成")
    print(f"导入数据统计: {inserted_counts}")
    
    return {
        "file": file_path,
        "success": True,
        "inserted_counts": inserted_counts
    }

# 导入result_all_data_in_1下的heat_transfer.csv文件
async def import_heat_transfer_data(file_path):
    """导入heat_transfer.csv文件数据
    
    Args:
        file_path (str): 文件路径
        
    Returns:
        dict: 导入结果统计
    """
    print(f"开始导入文件: {file_path}")
    
    # 读取CSV文件
    df = read_csv_file(file_path)
    if df is None:
        return {"file": file_path, "success": False, "message": "读取文件失败"}
    
    # 初始化数据列表
    performance_data = []
    k_prediction_data = []
    
    # 处理每行数据
    for _, row in df.iterrows():
        # 获取day和hour
        day = row.get('day', 0)
        hour = row.get('hour', 0)
        
        # 转换为时间戳
        timestamp = convert_to_timestamp(day, hour)
        
        # 处理points和side
        # 从position或points字段获取
        points = row.get('position', row.get('points', ''))
        # 如果是字符串，尝试转换为整数
        if isinstance(points, str):
            try:
                points = int(float(points))
            except ValueError:
                continue
        elif isinstance(points, float):
            points = int(points)
        
        # 默认为管侧
        side = 'tube'
        
        # 换热器编号，默认为1
        heat_exchanger_id = 1
        
        # 1. 性能参数数据
        performance_param = PerformanceParameter(
            heat_exchanger_id=heat_exchanger_id,
            timestamp=timestamp,
            points=points,
            side=side,
            K=row.get('K_actual'),
            alpha_i=row.get('alpha_i'),
            alpha_o=row.get('alpha_o')
        )
        performance_data.append(performance_param)
        
        # 2. K_predicted数据
        k_predicted = row.get('K_predicted')
        if not pd.isna(k_predicted):
            k_pred_data = KPrediction(
                heat_exchanger_id=heat_exchanger_id,
                timestamp=timestamp,
                points=points,
                side=side,
                K_predicted=k_predicted
            )
            k_prediction_data.append(k_pred_data)
    
    # 批量插入数据
    inserted_counts = {}
    
    if performance_data:
        inserted_counts['performance_parameters'] = await batch_insert(PerformanceParameter, performance_data, IMPORT_CONFIG['batch_size'])
    
    if k_prediction_data:
        inserted_counts['k_predictions'] = await batch_insert(KPrediction, k_prediction_data, IMPORT_CONFIG['batch_size'])
    
    print(f"文件 {file_path} 导入完成")
    print(f"导入数据统计: {inserted_counts}")
    
    return {
        "file": file_path,
        "success": True,
        "inserted_counts": inserted_counts
    }

# 导入result_all_data_in_1/nonlinear_regression/daily_parameters/day_X_params.csv文件
async def import_model_params(file_path):
    """导入模型参数文件数据
    
    Args:
        file_path (str): 文件路径
        
    Returns:
        dict: 导入结果统计
    """
    print(f"开始导入文件: {file_path}")
    
    # 读取CSV文件
    df = read_csv_file(file_path)
    if df is None:
        return {"file": file_path, "success": False, "message": "读取文件失败"}
    
    # 初始化数据列表
    model_param_data = []
    
    # 处理每行数据
    for _, row in df.iterrows():
        # 获取day
        day = row.get('day', 0)
        
        # 每天3点更新，所以hour=3
        timestamp = convert_to_timestamp(day, 3)
        
        # 换热器编号，默认为1
        heat_exchanger_id = 1
        
        # 创建模型参数数据
        model_param = ModelParameter(
            heat_exchanger_id=heat_exchanger_id,
            timestamp=timestamp,
            a=row.get('a'),
            p=row.get('p'),
            b=row.get('b')
        )
        model_param_data.append(model_param)
    
    # 批量插入数据
    inserted_counts = {}
    
    if model_param_data:
        inserted_counts['model_parameters'] = await batch_insert(ModelParameter, model_param_data, IMPORT_CONFIG['batch_size'])
    
    print(f"文件 {file_path} 导入完成")
    print(f"导入数据统计: {inserted_counts}")
    
    return {
        "file": file_path,
        "success": True,
        "inserted_counts": inserted_counts
    }

# 主导入函数
async def main():
    """主导入函数"""
    print("=== 开始数据导入 ===")
    print(f"当前时间: {datetime.now()}")
    print(f"数据源路径: {DATA_SOURCE_PATHS}")
    print(f"导入配置: {IMPORT_CONFIG}")
    
    # 初始化数据库连接
    await init_db()
    
    try:
        # 结果统计
        total_results = []
        
        # 1. 导入cache目录下的full_data.csv文件
        cache_files = get_all_csv_files(DATA_SOURCE_PATHS['cache'])
        cache_full_data_files = [f for f in cache_files if 'full_data' in f]
        print(f"\n找到 {len(cache_full_data_files)} 个cache full_data文件")
        
        for file_path in cache_full_data_files:
            result = await import_cache_full_data(file_path)
            total_results.append(result)
        
        # 2. 导入two_stage_linear下的heat_transfer.csv文件
        heat_transfer_dir = os.path.join(DATA_SOURCE_PATHS['result_all_data_in_1'], 'two_stage_linear', 'heat_transfer_coefficients')
        if os.path.exists(heat_transfer_dir):
            heat_transfer_files = get_all_csv_files(heat_transfer_dir)
            print(f"\n找到 {len(heat_transfer_files)} 个two_stage_linear heat_transfer文件")
            
            for file_path in heat_transfer_files:
                result = await import_heat_transfer_data(file_path)
                total_results.append(result)
        
        # 3. 导入nonlinear_regression下的heat_transfer.csv文件（K预测值）
        nonlinear_regression_dir = os.path.join(DATA_SOURCE_PATHS['result'], 'nonlinear_regression')
        if os.path.exists(nonlinear_regression_dir):
            # 获取所有points_TX.0文件夹
            points_dirs = [d for d in os.listdir(nonlinear_regression_dir) if os.path.isdir(os.path.join(nonlinear_regression_dir, d)) and d.startswith('points_T')]
            print(f"\n找到 {len(points_dirs)} 个points文件夹")
            
            for points_dir in points_dirs:
                points_path = os.path.join(nonlinear_regression_dir, points_dir)
                heat_transfer_coeff_dir = os.path.join(points_path, 'heat_transfer_coefficients')
                
                if os.path.exists(heat_transfer_coeff_dir):
                    heat_transfer_files = get_all_csv_files(heat_transfer_coeff_dir)
                    print(f"\n在 {points_dir} 中找到 {len(heat_transfer_files)} 个heat_transfer文件")
                    
                    for file_path in heat_transfer_files:
                        result = await import_heat_transfer_data(file_path)
                        total_results.append(result)
        
        # 4. 导入模型参数文件
        model_params_dir = os.path.join(DATA_SOURCE_PATHS['result_all_data_in_1'], 'nonlinear_regression', 'daily_parameters')
        if os.path.exists(model_params_dir):
            model_param_files = get_all_csv_files(model_params_dir)
            print(f"\n找到 {len(model_param_files)} 个模型参数文件")
            
            for file_path in model_param_files:
                result = await import_model_params(file_path)
                total_results.append(result)
        
        # 5. 导入data目录下的operation_parameters.csv和performance_parameters.csv文件
        data_dir = DATA_SOURCE_PATHS['data']
        if os.path.exists(data_dir):
            data_files = get_all_csv_files(data_dir)
            operation_files = [f for f in data_files if 'operation_parameters' in f]
            performance_files = [f for f in data_files if 'performance_parameters' in f]
            
            print(f"\n找到 {len(operation_files)} 个operation_parameters文件")
            print(f"找到 {len(performance_files)} 个performance_parameters文件")
            
            # TODO: 实现这两种文件的导入逻辑
        
        # 打印导入结果汇总
        print("\n=== 导入结果汇总 ===")
        success_count = 0
        for result in total_results:
            if result['success']:
                success_count += 1
                print(f"✓ {result['file']}: {result['inserted_counts']}")
            else:
                print(f"✗ {result['file']}: {result.get('message', '导入失败')}")
        
        print(f"\n总文件数: {len(total_results)}")
        print(f"成功导入: {success_count}")
        print(f"失败导入: {len(total_results) - success_count}")
        
        print("\n=== 数据导入完成 ===")
        print(f"结束时间: {datetime.now()}")
        
    except Exception as e:
        print(f"\n导入过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # 关闭数据库连接
        await close_db()

# 运行主函数
if __name__ == "__main__":
    asyncio.run(main())
