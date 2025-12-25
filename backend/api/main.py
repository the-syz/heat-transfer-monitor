from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import sys
import os
import json
from datetime import datetime

# 添加backend目录到Python路径
# main.py在backend/api/目录下，需要添加backend目录本身到路径
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, backend_dir)

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
# 使用相对于backend目录的路径
CONFIG_FILE = os.path.join(backend_dir, "config", "config.json")
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
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "code": "DATA_PROCESSING_FAILED",
                    "type": "InternalServerError",
                    "message": "数据处理失败",
                    "timestamp": datetime.now().isoformat()
                }
            )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "INVALID_PARAMETERS",
                "type": "BadRequest",
                "message": str(e),
                "timestamp": datetime.now().isoformat()
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INTERNAL_SERVER_ERROR",
                "type": "InternalServerError",
                "message": str(e),
                "timestamp": datetime.now().isoformat()
            }
        )

@app.get("/operation-parameters", summary="获取运行参数", description="获取运行参数数据")
async def get_operation_parameters(heat_exchanger_id: int = None, day: int = None, hour: int = None):
    try:
        # 验证参数
        if day and (day < 1 or day > 31):
            raise ValueError("day参数必须在1-31之间")
        if hour is not None and (hour < 0 or hour > 23):
            raise ValueError("hour参数必须在0-23之间")
        
        # 构建查询条件
        query = "SELECT * FROM operation_parameters WHERE 1=1"
        params = []
        
        if heat_exchanger_id:
            query += " AND heat_exchanger_id = %s"
            params.append(heat_exchanger_id)
        
        # 处理day和hour参数，转换为timestamp范围查询
        if day:
            if hour is not None:
                # 查询特定天和小时的数据
                start_time = f"2022-01-{day:02d} {hour:02d}:00:00"
                end_time = f"2022-01-{day:02d} {hour:02d}:59:59"
                query += " AND timestamp BETWEEN %s AND %s"
                params.extend([start_time, end_time])
            else:
                # 查询特定天的数据
                start_time = f"2022-01-{day:02d} 00:00:00"
                end_time = f"2022-01-{day:02d} 23:59:59"
                query += " AND timestamp BETWEEN %s AND %s"
                params.extend([start_time, end_time])
        elif hour is not None:
            # 只查询特定小时的数据（所有天）
            query += " AND HOUR(timestamp) = %s"
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
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "code": "QUERY_EXECUTION_FAILED",
                    "type": "InternalServerError",
                    "message": "数据库查询执行失败",
                    "timestamp": datetime.now().isoformat()
                }
            )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "INVALID_PARAMETERS",
                "type": "BadRequest",
                "message": str(e),
                "timestamp": datetime.now().isoformat()
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INTERNAL_SERVER_ERROR",
                "type": "InternalServerError",
                "message": str(e),
                "timestamp": datetime.now().isoformat()
            }
        )

@app.get("/physical-parameters", summary="获取物理参数", description="获取物理参数数据")
async def get_physical_parameters(heat_exchanger_id: int = None, day: int = None, hour: int = None):
    try:
        # 验证参数
        if day and (day < 1 or day > 31):
            raise ValueError("day参数必须在1-31之间")
        if hour is not None and (hour < 0 or hour > 23):
            raise ValueError("hour参数必须在0-23之间")
        
        # 构建查询条件
        query = "SELECT * FROM physical_parameters WHERE 1=1"
        params = []
        
        if heat_exchanger_id:
            query += " AND heat_exchanger_id = %s"
            params.append(heat_exchanger_id)
        
        # 处理day和hour参数，转换为timestamp范围查询
        if day:
            if hour is not None:
                # 查询特定天和小时的数据
                start_time = f"2022-01-{day:02d} {hour:02d}:00:00"
                end_time = f"2022-01-{day:02d} {hour:02d}:59:59"
                query += " AND timestamp BETWEEN %s AND %s"
                params.extend([start_time, end_time])
            else:
                # 查询特定天的数据
                start_time = f"2022-01-{day:02d} 00:00:00"
                end_time = f"2022-01-{day:02d} 23:59:59"
                query += " AND timestamp BETWEEN %s AND %s"
                params.extend([start_time, end_time])
        elif hour is not None:
            # 只查询特定小时的数据（所有天）
            query += " AND HOUR(timestamp) = %s"
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
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "code": "QUERY_EXECUTION_FAILED",
                    "type": "InternalServerError",
                    "message": "数据库查询执行失败",
                    "timestamp": datetime.now().isoformat()
                }
            )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "INVALID_PARAMETERS",
                "type": "BadRequest",
                "message": str(e),
                "timestamp": datetime.now().isoformat()
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INTERNAL_SERVER_ERROR",
                "type": "InternalServerError",
                "message": str(e),
                "timestamp": datetime.now().isoformat()
            }
        )

@app.get("/k-management", summary="获取K管理数据", description="获取K_lmtd数据")
async def get_k_management(heat_exchanger_id: int = None, day: int = None, hour: int = None):
    try:
        # 验证参数
        if day and (day < 1 or day > 31):
            raise ValueError("day参数必须在1-31之间")
        if hour is not None and (hour < 0 or hour > 23):
            raise ValueError("hour参数必须在0-23之间")
        
        # 构建查询条件
        query = "SELECT * FROM k_management WHERE 1=1"
        params = []
        
        if heat_exchanger_id:
            query += " AND heat_exchanger_id = %s"
            params.append(heat_exchanger_id)
        
        # 处理day和hour参数，转换为timestamp范围查询
        if day:
            if hour is not None:
                # 查询特定天和小时的数据
                start_time = f"2022-01-{day:02d} {hour:02d}:00:00"
                end_time = f"2022-01-{day:02d} {hour:02d}:59:59"
                query += " AND timestamp BETWEEN %s AND %s"
                params.extend([start_time, end_time])
            else:
                # 查询特定天的数据
                start_time = f"2022-01-{day:02d} 00:00:00"
                end_time = f"2022-01-{day:02d} 23:59:59"
                query += " AND timestamp BETWEEN %s AND %s"
                params.extend([start_time, end_time])
        elif hour is not None:
            # 只查询特定小时的数据（所有天）
            query += " AND HOUR(timestamp) = %s"
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
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "code": "QUERY_EXECUTION_FAILED",
                    "type": "InternalServerError",
                    "message": "数据库查询执行失败",
                    "timestamp": datetime.now().isoformat()
                }
            )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "INVALID_PARAMETERS",
                "type": "BadRequest",
                "message": str(e),
                "timestamp": datetime.now().isoformat()
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INTERNAL_SERVER_ERROR",
                "type": "InternalServerError",
                "message": str(e),
                "timestamp": datetime.now().isoformat()
            }
        )

@app.get("/performance", summary="获取性能数据", description="获取换热器性能数据")
async def get_performance(heat_exchanger_id: int = None, day: int = None, hour: int = None):
    try:
        # 验证参数
        if day and (day < 1 or day > 31):
            raise ValueError("day参数必须在1-31之间")
        if hour is not None and (hour < 0 or hour > 23):
            raise ValueError("hour参数必须在0-23之间")
        
        # 构建查询条件
        query = "SELECT * FROM performance_parameters WHERE 1=1"
        params = []
        
        if heat_exchanger_id:
            query += " AND heat_exchanger_id = %s"
            params.append(heat_exchanger_id)
        
        # 处理day和hour参数，转换为timestamp范围查询
        if day:
            if hour is not None:
                # 查询特定天和小时的数据
                start_time = f"2022-01-{day:02d} {hour:02d}:00:00"
                end_time = f"2022-01-{day:02d} {hour:02d}:59:59"
                query += " AND timestamp BETWEEN %s AND %s"
                params.extend([start_time, end_time])
            else:
                # 查询特定天的数据
                start_time = f"2022-01-{day:02d} 00:00:00"
                end_time = f"2022-01-{day:02d} 23:59:59"
                query += " AND timestamp BETWEEN %s AND %s"
                params.extend([start_time, end_time])
        elif hour is not None:
            # 只查询特定小时的数据（所有天）
            query += " AND HOUR(timestamp) = %s"
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
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "code": "QUERY_EXECUTION_FAILED",
                    "type": "InternalServerError",
                    "message": "数据库查询执行失败",
                    "timestamp": datetime.now().isoformat()
                }
            )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "INVALID_PARAMETERS",
                "type": "BadRequest",
                "message": str(e),
                "timestamp": datetime.now().isoformat()
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INTERNAL_SERVER_ERROR",
                "type": "InternalServerError",
                "message": str(e),
                "timestamp": datetime.now().isoformat()
            }
        )

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
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "FETCH_HEAT_EXCHANGERS_FAILED",
                "type": "InternalServerError",
                "message": str(e),
                "timestamp": datetime.now().isoformat()
            }
        )

@app.get("/model-parameters", summary="获取模型参数", description="获取模型参数数据")
async def get_model_parameters(heat_exchanger_id: int = None, day: int = None):
    try:
        # 验证参数
        if day and (day < 1 or day > 365):
            raise ValueError("day参数必须在1-365之间")
        
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
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "code": "QUERY_EXECUTION_FAILED",
                    "type": "InternalServerError",
                    "message": "数据库查询执行失败",
                    "timestamp": datetime.now().isoformat()
                }
            )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "INVALID_PARAMETERS",
                "type": "BadRequest",
                "message": str(e),
                "timestamp": datetime.now().isoformat()
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INTERNAL_SERVER_ERROR",
                "type": "InternalServerError",
                "message": str(e),
                "timestamp": datetime.now().isoformat()
            }
        )

@app.get("/calculate-performance/{day}/{hour}", summary="计算指定时间的性能", description="计算指定天数和小时的换热器性能")
async def calculate_performance(day: int, hour: int):
    try:
        # 验证参数
        if day < 1 or day > 365:
            raise ValueError("day参数必须在1-365之间")
        if hour < 0 or hour > 23:
            raise ValueError("hour参数必须在0-23之间")
            
        success = calculator.run_calculation(day, hour)
        if success:
            return {
                "status": "success",
                "message": f"第{day}天第{hour}小时的性能计算完成",
                "day": day,
                "hour": hour
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "code": "PERFORMANCE_CALCULATION_FAILED",
                    "type": "InternalServerError",
                    "message": "性能计算失败",
                    "timestamp": datetime.now().isoformat()
                }
            )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "INVALID_PARAMETERS",
                "type": "BadRequest",
                "message": str(e),
                "timestamp": datetime.now().isoformat()
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INTERNAL_SERVER_ERROR",
                "type": "InternalServerError",
                "message": str(e),
                "timestamp": datetime.now().isoformat()
            }
        )

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )