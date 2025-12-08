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
        timestamp = convert