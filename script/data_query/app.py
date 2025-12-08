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
            "points": pp.points,
            "density": pp.density,
            "viscosity": pp.viscosity,
            "thermal_conductivity": pp.thermal_conductivity,
            "specific_heat": pp.specific_heat,
            "reynolds": pp.reynolds,
            "prandtl": pp.prandtl
        })
    
    # 查询性能参数
    performance_params = await PerformanceParameter.filter(
        heat_exchanger_id=heat_exchanger_id,
        side=side,
        timestamp__range=(start_time, end_time)
    ).all()
    
    for perf in performance_params:
        results["performance"].append({
            "timestamp": perf.timestamp,
            "points": perf.points,
            "K": perf.K,
            "alpha_i": perf.alpha_i,
            "alpha_o": perf.alpha_o,
            "heat_duty": perf.heat_duty,
            "effectiveness": perf.effectiveness,
            "lmtd": perf.lmtd
        })
    
    # 查询K预测值
    k_predictions = await KPrediction.filter(
        heat_exchanger_id=heat_exchanger_id,
        side=side,
        timestamp__range=(start_time, end_time)
    ).all()
    
    for kp in k_predictions:
        results["k_prediction"].append({
            "timestamp": kp.timestamp,
            "points": kp.points,
            "K_predicted": kp.K_predicted
        })
    
    # 查询模型参数
    # 模型参数每天更新一次，查询当天的数据
    model_params = await ModelParameter.filter(
        heat_exchanger_id=heat_exchanger_id,
        timestamp__date=selected_date
    ).all()
    
    for mp in model_params:
        results["model"].append({
            "timestamp": mp.timestamp,
            "a": mp.a,
            "p": mp.p,
            "b": mp.b
        })
    
    return results

# 获取所有换热器列表
async def get_heat_exchangers():
    """获取所有换热器列表"""
    heat_exchangers = await HeatExchanger.all().order_by("id").all()
    return [(he.id, f"换热器 {he.id} - {he.type}") for he in heat_exchangers]

# 将结果转换为DataFrame

def results_to_dataframes(results):
    """将查询结果转换为DataFrame"""
    dataframes = {}
    
    for key, data in results.items():
        if data:
            df = pd.DataFrame(data)
            # 按points和timestamp排序
            df = df.sort_values(by=["points", "timestamp"])
            dataframes[key] = df
        else:
            dataframes[key] = pd.DataFrame()
    
    return dataframes

# 异步查询包装函数
def async_query_wrapper(heat_exchanger_id, side, selected_date, selected_time):
    """异步查询包装函数，用于在同步环境中调用"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        loop.run_until_complete(init_db())
        results = loop.run_until_complete(query_data(heat_exchanger_id, side, selected_date, selected_time))
        return results
    finally:
        loop.run_until_complete(close_db())
        loop.close()

# 获取换热器列表包装函数
def get_heat_exchangers_wrapper():
    """获取换热器列表包装函数"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        loop.run_until_complete(init_db())
        heat_exchangers = loop.run_until_complete(get_heat_exchangers())
        return heat_exchangers
    finally:
        loop.run_until_complete(close_db())
        loop.close()

# 主应用

def main():
    """主应用"""
    st.set_page_config(
        page_title="换热器监测系统数据查询",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # 应用标题
    st.title("📊 换热器监测系统数据查询")
    st.markdown("---")
    
    # 侧边栏
    st.sidebar.header("查询参数")
    
    # 获取换热器列表
    heat_exchangers = get_heat_exchangers_wrapper()
    
    if not heat_exchangers:
        st.error("未找到换热器数据")
        return
    
    # 选择换热器
    heat_exchanger_options = {he[0]: he[1] for he in heat_exchangers}
    selected_he_id = st.sidebar.selectbox(
        "选择换热器",
        list(heat_exchanger_options.keys()),
        format_func=lambda x: heat_exchanger_options[x]
    )
    
    # 选择管侧/壳侧
    side = st.sidebar.selectbox(
        "选择侧标识",
        ["tube", "shell"],
        format_func=lambda x: "管侧" if x == "tube" else "壳侧"
    )
    
    # 选择日期
    selected_date = st.sidebar.date_input(
        "选择日期",
        value=datetime(2022, 1, 1),
        min_value=datetime(2022, 1, 1),
        max_value=datetime(2024, 12, 31)
    )
    
    # 选择时间
    selected_time = st.sidebar.time_input(
        "选择时间",
        value=datetime(2022, 1, 1, 0, 0).time()
    )
    
    # 查询按钮
    query_button = st.sidebar.button("🔍 查询数据")
    
    # 查询结果显示
    if query_button:
        st.markdown(f"### 查询结果")
        st.markdown(f"**换热器**: {heat_exchanger_options[selected_he_id]}")
        st.markdown(f"**侧标识**: {'管侧' if side == 'tube' else '壳侧'}")
        st.markdown(f"**日期**: {selected_date.strftime('%Y-%m-%d')}")
        st.markdown(f"**时间**: {selected_time.strftime('%H:%M:%S')}")
        st.markdown("---")
        
        # 查询数据
        with st.spinner("正在查询数据..."):
            results = async_query_wrapper(selected_he_id, side, selected_date, selected_time)
            dataframes = results_to_dataframes(results)
        
        # 显示结果
        tabs = st.tabs(["运行参数", "物性参数", "性能参数", "K预测值", "模型参数"])
        
        # 运行参数
        with tabs[0]:
            if not dataframes["operation"].empty:
                st.subheader("运行参数")
                st.dataframe(dataframes["operation"], use_container_width=True)
            else:
                st.info("未找到运行参数数据")
        
        # 物性参数
        with tabs