import os
import csv
from datetime import datetime, timedelta
import pandas as pd
from tortoise import Tortoise

from config import DATABASE_CONFIG, BASE_DATE

# 初始化Tortoise ORM
async def init_db():
    await Tortoise.init(
        db_url=DATABASE_CONFIG['url'],
        modules=DATABASE_CONFIG['modules']
    )

# 关闭数据库连接
async def close_db():
    await Tortoise.close_connections()

# 解析points字段，转换为整型，并确定side

def process_points(points_str):
    """将字符串格式的points转换为整型，并确定side
    
    Args:
        points_str (str): 原始points字符串，如"T10.0"或"S2.0"
        
    Returns:
        tuple: (points_int, side)
            points_int: 整型的points值
            side: 侧标识，"tube"或"shell"
    """
    if not points_str:
        return None, None
    
    # 去除前后空格
    points_str = points_str.strip()
    
    # 根据前缀确定side
    if points_str.startswith('T') or points_str.startswith('t'):
        side = 'tube'
        # 提取数字部分
        num_part = points_str[1:]
    elif points_str.startswith('S') or points_str.startswith('s'):
        side = 'shell'
        # 提取数字部分
        num_part = points_str[1:]
    else:
        # 如果没有前缀，默认作为管侧
        side = 'tube'
        num_part = points_str
    
    # 转换为整型
    try:
        points_int = int(float(num_part))
        return points_int, side
    except (ValueError, TypeError):
        return None, None

# 将day和hour转换为时间戳
def convert_to_timestamp(day, hour):
    """将day和hour转换为时间戳
    
    Args:
        day (int): 天数，从0开始
        hour (int): 小时数，0-23
        
    Returns:
        datetime: 转换后的时间戳
    """
    base_time = datetime.strptime(BASE_DATE, '%Y-%m-%d %H:%M:%S')
    return base_time + timedelta(days=day, hours=hour)

# 读取CSV文件
def read_csv_file(file_path):
    """读取CSV文件，返回DataFrame
    
    Args:
        file_path (str): CSV文件路径
        
    Returns:
        pd.DataFrame: 读取的数据
    """
    try:
        df = pd.read_csv(file_path)
        return df
    except Exception as e:
        print(f"读取CSV文件失败: {file_path}, 错误: {e}")
        return None

# 批量导入数据到数据库
async def batch_insert(model_class, data_list, batch_size=1000):
    """批量插入数据到数据库
    
    Args:
        model_class: Tortoise模型类
        data_list (list): 要插入的数据列表
        batch_size (int): 批量大小
        
    Returns:
        int: 插入的数据条数
    """
    if not data_list:
        return 0
    
    inserted_count = 0
    for i in range(0, len(data_list), batch_size):
        batch = data_list[i:i+batch_size]
        await model_class.bulk_create(batch)
        inserted_count += len(batch)
    
    return inserted_count

# 获取所有CSV文件路径
def get_all_csv_files(directory):
    """获取目录下所有CSV文件的路径
    
    Args:
        directory (str): 目录路径
        
    Returns:
        list: CSV文件路径列表
    """
    csv_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.csv'):
                csv_files.append(os.path.join(root, file))
    return csv_files

# 解析文件名，获取day信息
def get_day_from_filename(filename):
    """从文件名中提取day信息
    
    Args:
        filename (str): 文件名，如"day_5_full_data.csv"
        
    Returns:
        int: day值
    """
    try:
        # 提取day_后的数字
        basename = os.path.basename(filename)
        if basename.startswith('day_'):
            day_part = basename.split('_')[1]
            # 去除可能的后缀
            day_str = day_part.split('.')[0]
            return int(day_str)
        return None
    except (IndexError, ValueError):
        return None
