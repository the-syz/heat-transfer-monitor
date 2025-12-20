import pandas as pd
import numpy as np
from datetime import datetime
from pyfluids import Fluid, FluidsList

class DataLoader:
    def __init__(self, db_connection):
        self.db_conn = db_connection
    
    def get_operation_parameters_by_hour(self, day, hour):
        """根据天数和小时从测试数据库读取运行参数"""
        # 计算时间范围
        start_date = f"2022-01-{day} {hour}:00:00"
        end_date = f"2022-01-{day} {hour}:59:59"
        
        query = """SELECT * FROM operation_parameters 
                   WHERE timestamp BETWEEN %s AND %s"""
        params = (start_date, end_date)
        
        if self.db_conn.execute_query(self.db_conn.test_cursor, query, params):
            return self.db_conn.fetch_all(self.db_conn.test_cursor)
        return []
    
    def get_physical_parameters_by_hour(self, day, hour):
        """根据天数和小时从测试数据库读取物理参数"""
        # 计算时间范围
        start_date = f"2022-01-{day} {hour}:00:00"
        end_date = f"2022-01-{day} {hour}:59:59"
        
        query = """SELECT * FROM physical_parameters 
                   WHERE timestamp BETWEEN %s AND %s"""
        params = (start_date, end_date)
        
        if self.db_conn.execute_query(self.db_conn.test_cursor, query, params):
            return self.db_conn.fetch_all(self.db_conn.test_cursor)
        return []
    
    def insert_operation_parameters(self, data):
        """将运行参数插入到生产数据库"""
        if not data:
            return True
        
        # 构建插入语句，使用INSERT IGNORE避免重复主键错误
        columns = ', '.join(data[0].keys())
        placeholders = ', '.join(['%s'] * len(data[0]))
        query = f"INSERT IGNORE INTO operation_parameters ({columns}) VALUES ({placeholders})"
        
        # 准备数据
        values = []
        for record in data:
            values.append(tuple(record.values()))
        
        try:
            # 批量插入到生产数据库
            self.db_conn.prod_cursor.executemany(query, values)
            self.db_conn.commit(self.db_conn.prod_db)
            return True
        except Exception as e:
            print(f"插入运行参数失败: {e}")
            self.db_conn.rollback(self.db_conn.prod_db)
            return False
    
    def insert_physical_parameters(self, data):
        """将物理参数插入到生产数据库"""
        if not data:
            return True
        
        # 构建插入语句，使用INSERT IGNORE避免重复主键错误
        columns = ', '.join(data[0].keys())
        placeholders = ', '.join(['%s'] * len(data[0]))
        query = f"INSERT IGNORE INTO physical_parameters ({columns}) VALUES ({placeholders})"
        
        # 准备数据
        values = []
        for record in data:
            values.append(tuple(record.values()))
        
        try:
            # 批量插入
            self.db_conn.prod_cursor.executemany(query, values)
            self.db_conn.commit(self.db_conn.prod_db)
            return True
        except Exception as e:
            print(f"插入物理参数失败: {e}")
            self.db_conn.rollback(self.db_conn.prod_db)
            return False
    
    def get_performance_parameters_by_hour(self, day, hour):
        """根据天数和小时从测试数据库读取性能参数"""
        # 计算时间范围
        start_date = f"2022-01-{day} {hour}:00:00"
        end_date = f"2022-01-{day} {hour}:59:59"
        
        query = """
        SELECT * FROM performance_parameters 
        WHERE timestamp BETWEEN %s AND %s
        """
        params = (start_date, end_date)
        
        if self.db_conn.execute_query(self.db_conn.test_cursor, query, params):
            return self.db_conn.fetch_all(self.db_conn.test_cursor)
        return []
    
    def insert_k_management(self, data):
        """将K_lmtd插入到生产数据库的k_management表"""
        if not data:
            return True
        
        # 构建插入语句
        columns = ', '.join(data[0].keys())
        placeholders = ', '.join(['%s'] * len(data[0]))
        
        # 构建ON DUPLICATE KEY UPDATE子句
        update_clause = ', '.join([f"{col} = VALUES({col})" for col in data[0].keys()])
        query = f"INSERT INTO k_management ({columns}) VALUES ({placeholders}) ON DUPLICATE KEY UPDATE {update_clause}"
        
        # 准备数据
        values = []
        for record in data:
            values.append(tuple(record.values()))
        
        try:
            # 批量插入
            self.db_conn.prod_cursor.executemany(query, values)
            self.db_conn.commit(self.db_conn.prod_db)
            return True
        except Exception as e:
            print(f"插入k_management失败: {e}")
            self.db_conn.rollback(self.db_conn.prod_db)
            return False
    
    def insert_performance_parameters(self, data):
        """将性能参数插入到生产数据库"""
        if not data:
            return True
        
        # 构建插入语句
        columns = ', '.join(data[0].keys())
        placeholders = ', '.join(['%s'] * len(data[0]))
        query = f"INSERT INTO performance_parameters ({columns}) VALUES ({placeholders})"
        
        # 准备数据
        values = []
        for record in data:
            values.append(tuple(record.values()))
        
        try:
            # 批量插入
            self.db_conn.prod_cursor.executemany(query, values)
            self.db_conn.commit(self.db_conn.prod_db)
            return True
        except Exception as e:
            print(f"插入性能参数失败: {e}")
            self.db_conn.rollback(self.db_conn.prod_db)
            return False
    
    def get_water_properties(self, temperature_celsius):
        """根据温度计算水的物性参数（使用pyfluids库）"""
        try:
            # 确保温度在合理范围内
            temp = max(0, min(temperature_celsius, 100))
            
            # 使用pyFluids库计算水的物性参数
            try:
                # 方法1：直接使用构造函数设置状态
                water = Fluid(FluidsList.Water, temperature=temp, pressure=101325)  # 101325 Pa = 1 atm
            except (TypeError, ValueError):
                try:
                    # 方法2：尝试使用其他参数组合
                    water = Fluid(FluidsList.Water)
                    water.with_state(T=temp + 273.15, P=1.01325)
                except (TypeError, ValueError):
                        # 如果所有尝试都失败，使用默认值
                        return {
                            'rho': 1000,  # kg/m³
                            'mu': 0.001,  # Pa·s
                            'lambda': 0.6,  # W/(m·K)
                            'Cp': 4186    # J/(kg·K)
                        }
            
            # 尝试获取物性参数
            rho = water.density
            mu = water.dynamic_viscosity
            lambda_val = water.thermal_conductivity
            cp = water.specific_heat
            
            # 确保所有参数都有效
            if all(param > 0 for param in [rho, mu, lambda_val, cp]):
                return {
                    'rho': rho,      # 密度 (kg/m³)
                    'mu': mu,        # 动力粘度 (Pa·s)
                    'lambda': lambda_val,  # 导热系数 (W/(m·K))
                    'Cp': cp         # 比热容 (J/(kg·K))
                }
        except Exception as e:
            print(f"计算水的物性参数失败: {e}")
        
        # 使用默认值，但根据温度做简单调整
        temp_adjusted = temp - 25  # 以25°C为基准
        return {
            'rho': 1000 - 0.2 * temp_adjusted,  # 密度 (kg/m³)
            'mu': 0.001 * np.exp(-0.02 * temp_adjusted),  # 动力粘度 (Pa·s)
            'lambda': 0.6 + 0.001 * temp_adjusted,  # 导热系数 (W/(m·K))
            'Cp': 4186 - 1 * temp_adjusted,  # 比热容 (J/(kg·K))
        }
    
    def calculate_reynolds_number(self, rho, u, d, mu):
        """计算雷诺数 Re = (rho * u * d) / mu"""
        try:
            if rho <= 0 or u <= 0 or d <= 0 or mu <= 0:
                return 0
            return (rho * u * d) / mu
        except Exception:
            return 0
    
    def calculate_prandtl_number(self, Cp, mu, lambda_val):
        """计算普朗特数 Pr = (Cp * mu) / lambda"""
        try:
            if Cp <= 0 or mu <= 0 or lambda_val <= 0:
                return 0
            return (Cp * mu) / lambda_val
        except Exception:
            return 0
    
    def process_operation_data(self, operation_data, physical_data, heat_exchanger=None):
        """处理运行数据，计算物理参数"""
        processed_data = []
        
        # 构建物理参数映射，方便查找
        physical_map = {}
        # 处理physical_data为None的情况
        if physical_data:
            for p_data in physical_data:
                key = (p_data['points'], p_data['side'])
                physical_map[key] = p_data
        
        # 获取管径，默认0.02m
        d_i = heat_exchanger.get('d_i_original', 0.02) if heat_exchanger else 0.02
        
        for op_data in operation_data:
            # 获取温度，用于计算水的物性参数
            temperature = op_data.get('temperature', 25)  # 默认25°C
            
            # 从pyfluids获取水的物性参数
            water_props = self.get_water_properties(temperature)
            
            # 从物理参数表获取导热系数
            key = (op_data['points'], op_data['side'])
            thermal_conductivity = physical_map.get(key, {}).get('thermal_conductivity', water_props['lambda'])
            
            # 计算雷诺数和普朗特数
            Re = self.calculate_reynolds_number(
                water_props['rho'], 
                op_data.get('velocity', 0), 
                d_i,  # 使用数据库中的管径或默认值
                water_props['mu']
            )
            
            Pr = self.calculate_prandtl_number(
                water_props['Cp'],
                water_props['mu'],
                thermal_conductivity
            )
            
            # 构建处理后的数据（使用数据库表中正确的字段名）
            processed = {
                'points': op_data['points'],
                'side': op_data['side'],
                'timestamp': op_data['timestamp'],
                'density': water_props['rho'],
                'viscosity': water_props['mu'],  # 使用viscosity而不是dynamic_viscosity
                'thermal_conductivity': thermal_conductivity,
                'specific_heat': water_props['Cp'],
                'reynolds': Re,  # 使用reynolds而不是reynolds_number
                'prandtl': Pr,  # 使用prandtl而不是prandtl_number
                'heat_exchanger_id': op_data.get('heat_exchanger_id', 1)
            }
            
            processed_data.append(processed)
        
        return processed_data
    
    def get_all_heat_exchangers(self):
        """获取所有换热器信息"""
        query = "SELECT * FROM heat_exchanger"
        
        if self.db_conn.execute_query(self.db_conn.prod_cursor, query):
            return self.db_conn.fetch_all(self.db_conn.prod_cursor)
        return []
    
    def get_training_data_for_stage1(self, training_days):
        """获取阶段1训练数据"""
        # 计算时间范围
        start_date = f"2022-01-01 00:00:00"
        end_date = f"2022-01-{training_days} 23:59:59"
        
        query = """
        SELECT p.*, k.K_actual
        FROM physical_parameters p
        JOIN k_management k ON p.heat_exchanger_id = k.heat_exchanger_id 
                           AND p.timestamp = k.timestamp 
                           AND p.points = k.points 
                           AND p.side = k.side
        WHERE p.timestamp BETWEEN %s AND %s
        """
        params = (start_date, end_date)
        
        if self.db_conn.execute_query(self.db_conn.prod_cursor, query, params):
            return self.db_conn.fetch_all(self.db_conn.prod_cursor)
        return []
    
    def insert_model_parameters(self, model_params, stage):
        """将模型参数插入到model_parameters表"""
        # 获取当前时间
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 构建数据
        data = {
            'timestamp': current_time,
            'a': model_params['a'],
            'p': model_params['p'],
            'b': model_params['b'],
            'stage': stage
        }
        
        # 构建插入语句
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['%s'] * len(data))
        query = f"INSERT INTO model_parameters ({columns}) VALUES ({placeholders})"
        
        try:
            # 插入到生产数据库
            self.db_conn.prod_cursor.execute(query, tuple(data.values()))
            self.db_conn.commit(self.db_conn.prod_db)
            return True
        except Exception as e:
            print(f"插入模型参数失败: {e}")
            self.db_conn.rollback(self.db_conn.prod_db)
            return False
    
    def get_test_performance_parameters_by_hour(self, day, hour):
        """根据天数和小时从测试数据库读取性能参数"""
        # 计算时间范围
        start_date = f"2022-01-{day} {hour}:00:00"
        end_date = f"2022-01-{day} {hour}:59:59"
        
        query = """
        SELECT * FROM performance_parameters 
        WHERE timestamp BETWEEN %s AND %s
        """
        params = (start_date, end_date)
        
        if self.db_conn.execute_query(self.db_conn.test_cursor, query, params):
            return self.db_conn.fetch_all(self.db_conn.test_cursor)
        return []
    
    def update_k_management_with_predicted(self, data):
        """更新k_management表的K_predicted字段"""
        if not data:
            return True
        
        # 构建更新语句
        query = """
        UPDATE k_management 
        SET K_predicted = %s 
        WHERE heat_exchanger_id = %s AND timestamp = %s AND points = %s AND side = %s
        """
        
        # 准备数据
        values = []
        for record in data:
            values.append((
                record.get('K_predicted', 0),
                record['heat_exchanger_id'],
                record['timestamp'],
                record['points'],
                record['side']
            ))
        
        try:
            # 批量更新
            self.db_conn.prod_cursor.executemany(query, values)
            self.db_conn.commit(self.db_conn.prod_db)
            return True
        except Exception as e:
            print(f"更新k_management失败: {e}")
            self.db_conn.rollback(self.db_conn.prod_db)
            return False
    
    def get_new_data_count_for_stage2(self, day, optimization_hours):
        """获取新一天的数据数量，用于判断是否进入阶段2优化"""
        # 计算时间范围
        start_date = f"2022-01-{day} 00:00:00"
        end_date = f"2022-01-{day} {optimization_hours-1}:59:59"
        
        query = """
        SELECT COUNT(*) as count
        FROM physical_parameters
        WHERE timestamp BETWEEN %s AND %s
        """
        params = (start_date, end_date)
        
        if self.db_conn.execute_query(self.db_conn.prod_cursor, query, params):
            result = self.db_conn.fetch_one(self.db_conn.prod_cursor)
            return result['count'] if result else 0
        return 0
    
    def get_optimization_data_for_stage2(self, day, optimization_hours):
        """获取阶段2优化数据"""
        # 计算时间范围
        start_date = f"2022-01-{day} 00:00:00"
        end_date = f"2022-01-{day} {optimization_hours-1}:59:59"
        
        query = """
        SELECT p.*, k.K_actual
        FROM physical_parameters p
        JOIN k_management k ON p.heat_exchanger_id = k.heat_exchanger_id 
                           AND p.timestamp = k.timestamp 
                           AND p.points = k.points 
                           AND p.side = k.side
        WHERE p.timestamp BETWEEN %s AND %s
        """
        params = (start_date, end_date)
        
        if self.db_conn.execute_query(self.db_conn.prod_cursor, query, params):
            return self.db_conn.fetch_all(self.db_conn.prod_cursor)
        return []
    
