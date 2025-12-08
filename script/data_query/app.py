import streamlit as st
import sys
import os
from datetime import datetime, timedelta
import asyncio
import pandas as pd

# 添加项目根目录到Python路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

# 数据库模型
from data.models import (
    HeatExchanger,
    OperationParameter,
    PhysicalParameter,
    PerformanceParameter,
    ModelParameter,
    KPrediction
)

# 数据库连接配置
DB_CONFIG = {
    'url': 'mysql://heatexMCP:123123@localhost:3306/heat_exchanger_monitor_db',
    'modules': {'models': ['data.models']}
}

# 初始化数据库连接
async def init_db():
    from tortoise import Tortoise
    await Tortoise.init(
        db_url=DB_CONFIG['url'],
        modules=DB_CONFIG['modules']
    )

# 关闭数据库连接
async def close_db():
    from tortoise import Tortoise
    await Tortoise.close_connections()

# 查询数据
async def query_data(heat_exchanger_id, side, selected_date, selected_time):
    """查询数据"""
    # 组合日期和时间
    query_timestamp = datetime.combine(selected_date, selected_time)
    
    # 查询±1小时范围内的数据
    start_time = query_timestamp - timedelta(hours=1)
    end_time = query_timestamp + timedelta(hours=1)
    
    # 查询各表数据
    results = {
        "operation": [],
        "physical": [],
        "performance": [],
        "k_prediction": [],
        "model": []
    }
    
    # 查询运行参数
    operation_params = await OperationParameter.filter(
        heat_exchanger_id=heat_exchanger_id,
        side=side,
        timestamp__range=(start_time, end_time)
    ).all()
    
    for op in operation_params:
        results["operation"].append({
            "timestamp": op.timestamp,
            "points": op.points,
            "temperature": op.temperature,
            "pressure": op.pressure,
            "flow_rate": op.flow_rate,
            "velocity": op.velocity
        })
    
    # 查询物性参数
    physical_params = await PhysicalParameter.filter(
        heat_exchanger_id=heat_exchanger_id,
        side=side,
        timestamp__range=(start_time, end_time)
    ).all()
    
    for pp in physical_params:
        results["physical"].append({
            "timestamp": pp.timestamp,
           