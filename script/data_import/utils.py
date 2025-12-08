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
    