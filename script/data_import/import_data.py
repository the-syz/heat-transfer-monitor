import sys
import os
from datetime import datetime
import asyncio

# 添加项目根目录到Python路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from data.models import (
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

# 导入result_all_data_in_1/two_stage_linear/heat_transfer_coefficients/day_X_heat_transfer.csv文件
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
        points_str = row.get('points', '')
        points, side = process_points(str(points_str))
        if points is None:
            continue
        
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
    