from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import json
import os
from datetime import datetime
from db.db_connection import DatabaseConnection
from calculation.main_calculator import MainCalculator

# 创建FastAPI应用
app = FastAPI(
    title="Heat Exchanger Monitor API",
    description="换热器性能监测API",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 加载配置
CONFIG_FILE = "../config/config.json"
with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
    config = json.load(f)

# 初始化计算器
calculator = MainCalculator(CONFIG_FILE)

@app.get("/health", summary="健康检查", description="检查API是否正常运行")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "heat_exchanger_monitor_api"
    }

@app.post("/process-data/{day}/{hour}", summary="处理指定时间的数据", description="处理指定天数和小时的数据")
async def process_data(day: int, hour: int):
    try:
        success = calculator.process_data_by_hour(day, hour)
        if success:
            return {
                "status": "success",
                "message": f"第{day}天第{hour}小时的数据处理完成",
                "day": day,
                "hour": hour
            }
        else:
            raise HTTPException(status_code=500, detail="数据处理失败")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/operation-parameters", summary="获取运行参数", description="获取运行参数数据")
async def get_operation_parameters(heat_exchanger_id: int = None, day: int = None, hour: int = None):
    try:
        # 构建查询条件
        query = "SELECT * FROM operation_parameters WHERE 1=1"
        params = []
        
        if heat_exchanger_id:
            query += " AND heat_exchanger_id = %s"
            params.append(heat_exchanger_id)
        if day:
            query += " AND day = %s"
            params.append(day)
        if hour:
            query += " AND hour = %s"
            params.append(hour)
        
        # 执行查询
        if calculator.db_conn.execute_query(calculator.db_conn.prod_cursor, query, params):
            result = calculator.db_conn.fetch_all(calculator.db_conn.prod_cursor)
            return {
                "status": "success",
                "count": len(result),
                "data": result
            }
        else:
            raise HTTPException(status_code=500, detail="查询失败")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/physical-parameters", summary="获取物理参数", description="获取物理参数数据")
async def get_physical_parameters(heat_exchanger_id: int = None, day: int = None, hour: int = None):
    try:
        # 构建查询条件
        query = "SELECT * FROM physical_parameters WHERE 1=1"
        params = []
        
        if heat_exchanger_id:
            query += " AND heat_exchanger_id = %s"
            params.append(heat_exchanger_id)
        if day:
            query += " AND day = %s"
            params.append(day)
        if hour:
            query += " AND hour = %s"
            params.append(hour)
        
        # 执行查询
        if calculator.db_conn.execute_query(calculator.db_conn.prod_cursor, query, params):
            result = calculator.db_conn.fetch_all(calculator.db_conn.prod_cursor)
            return {
                "status": "success",
                "count": len(result),
                "data": result
            }
        else:
            raise HTTPException(status_code=500, detail="查询失败")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/k-management", summary="获取K管理数据", description="获取K_lmtd数据")
async def get_k_management(heat_exchanger_id: int = None, day: int = None, hour: int = None):
    try:
        # 构建查询条件
        query = "SELECT * FROM k_management WHERE 1=1"
        params = []
        
        if heat_exchanger_id:
            query += " AND heat_exchanger_id = %s"
            params.append(heat_exchanger_id)
        if day:
            query += " AND day = %s"
            params.append(day)
        if hour:
            query += " AND hour = %s"
            params.append(hour)
        
        # 执行查询
        if calculator.db_conn.execute_query(calculator.db_conn.prod_cursor, query, params):
            result = calculator.db_conn.fetch_all(calculator.db_conn.prod_cursor)
            return {
                "status": "success",
                "count": len(result),
                "data": result
            }
        else:
            raise HTTPException(status_code=500, detail="查询失败")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/performance", summary="获取性能数据", description="获取换热器性能数据")
async def get_performance(heat_exchanger_id: int = None, day: int = None, hour: int = None):
    try:
        # 构建查询条件
        query = "SELECT * FROM performance_parameters WHERE 1=1"
        params = []
        
        if heat_exchanger_id:
            query += " AND heat_exchanger_id = %s"
            params.append(heat_exchanger_id)
        if day:
            query += " AND day = %s"
            params.append(day)
        if hour:
            query += " AND hour = %s"
            params.append(hour)
        
        # 执行查询
        if calculator.db_conn.execute_query(calculator.db_conn.prod_cursor, query, params):
            result = calculator.db_conn.fetch_all(calculator.db_conn.prod_cursor)
            return {
                "status": "success",
                "count": len(result),
                "data": result
            }
        else:
            raise HTTPException(status_code=500, detail="查询失败")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/heat-exchangers", summary="获取所有换热器", description="获取所有换热器信息")
async def get_heat_exchangers():
    try:
        heat_exchangers = calculator.data_loader.get_all_heat_exchangers()
        return {
            "status": "success",
            "count": len(heat_exchangers),
            "data": heat_exchangers
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/model-parameters", summary="获取模型参数", description="获取模型参数数据")
async def get_model_parameters(heat_exchanger_id: int = None, day: int = None):
    try:
        # 构建查询条件
        query = "SELECT * FROM model_parameters WHERE 1=1"
        params = []
        
        if heat_exchanger_id:
            query += " AND heat_exchanger_id = %s"
            params.append(heat_exchanger_id)
        if day:
            query += " AND day = %s"
            params.append(day)
        
        # 执行查询
        if calculator.db_conn.execute_query(calculator.db_conn.prod_cursor, query, params):
            result = calculator.db_conn.fetch_all(calculator.db_conn.prod_cursor)
            return {
                "status": "success",
                "count": len(result),
                "data": result
            }
        else:
            raise HTTPException(status_code=500, detail="查询失败")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/calculate-performance/{day}/{hour}", summary="计算指定时间的性能", description="计算指定天数和小时的换热器性能")
async def calculate_performance(day: int, hour: int):
    try:
        success = calculator.run_calculation(day, hour)
        if success:
            return {
                "status": "success",
                "message": f"第{day}天第{hour}小时的性能计算完成",
                "day": day,
                "hour": hour
            }
        else:
            raise HTTPException(status_code=500, detail="性能计算失败")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )