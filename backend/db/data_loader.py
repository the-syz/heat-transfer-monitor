import pandas as pd
import numpy as np
from datetime import datetime
from pyfluids import Fluid, FluidsList

class DataLoader:
    def __init__(self, db_connection):
        self.db_conn = db_connection
    
    def get_operation_parameters_by_hour(self, day, hour):
        """根据天数和小时从测试数据库读取运行参数"""
        # 计算时间范围，确保日期格式正确（day需要前导零）
        start_date = f"2022-01-{day:02d} {hour:02d}:00:00"
        end_date = f"2022-01-{day:02d} {hour:02d}:59:59"
        
        query = """SELECT * FROM operation_parameters 
                   WHERE timestamp BETWEEN %s AND %s"""
        params = (start_date, end_date)
        
        if self.db_conn.execute_query(self.db_conn.test_cursor, query, params):
            return self.db_conn.fetch_all(self.db_conn.test_cursor)
        return []
    
    def get_physical_parameters_by_hour(self, day, hour):
        """根据天数和小时从测试数据库读取物理参数"""
        # 计算时间范围，确保日期格式正确（day需要前导零）
        start_date = f"2022-01-{day:02d} {hour:02d}:00:00"
        end_date = f"2022-01-{day:02d} {hour:02d}:59:59"
        
        query = """SELECT * FROM physical_parameters 
                   WHERE timestamp BETWEEN %s AND %s"""
        params = (start_date, end_date)
        
        if self.db_conn.execute_query(self.db_conn.test_cursor, query, params):
            return self.db_conn.fetch_all(self.db_conn.test_cursor)
        return []
    
    def calculate_shell_equivalent_diameter(self, heat_exchanger):
        """计算壳侧等效直径
        
        对于转角正方形布置的管束，等效直径计算公式：
        De = 4 * (pt² - π*do²/4) / (π*do)
        
        参数:
            heat_exchanger: 换热器信息字典
        
        返回:
            De: 等效直径 (m)
        """
        try:
            # 获取参数
            tube_pitch = heat_exchanger.get('tube_pitch', 0.032)  # 管间距 (m)
            d_o = heat_exchanger.get('d_o', 0.025)  # 管外径 (m)
            
            # 计算等效直径
            # De = 4 * (pt² - π*do²/4) / (π*do)
            numerator = 4 * (tube_pitch ** 2 - np.pi * (d_o ** 2) / 4)
            denominator = np.pi * d_o
            
            if denominator <= 0:
                print(f"警告: 计算等效直径时分母为0或负数")
                return 0.02  # 返回默认值
            
            De = numerator / denominator
            
            return De if De > 0 else 0.02  # 如果计算结果无效，返回默认值
        except Exception as e:
            print(f"计算壳侧等效直径失败: {e}")
            return 0.02  # 返回默认值
    
    def calculate_shell_flow_area(self, heat_exchanger):
        """计算壳侧流通面积
        
        壳侧流通面积 = 壳体内径 × 折流板间距 × (1 - 管束占空比)
        简化计算：使用壳体内径和折流板间距
        
        参数:
            heat_exchanger: 换热器信息字典
        
        返回:
            A_shell: 壳侧流通面积 (m²)
        """
        try:
            shell_diameter = heat_exchanger.get('shell_inner_diameter', 0.7)  # 壳体内径 (m)
            baffle_spacing = heat_exchanger.get('baffle_spacing', 0.2)  # 折流板间距 (m)
            tube_count = heat_exchanger.get('tube_count', 268)  # 管数
            d_o = heat_exchanger.get('d_o', 0.025)  # 管外径 (m)
            
            # 计算管束占用的面积
            tube_bundle_area = tube_count * np.pi * (d_o ** 2) / 4
            
            # 计算壳侧横截面积
            shell_cross_section = np.pi * (shell_diameter ** 2) / 4
            
            # 计算流通面积（简化：使用折流板间距作为流通高度）
            # 更准确的计算需要考虑折流板切口和管束布置
            if shell_cross_section > 0:
                flow_area = shell_diameter * baffle_spacing * (1 - tube_bundle_area / shell_cross_section)
            else:
                flow_area = shell_diameter * baffle_spacing * 0.3  # 假设30%的流通面积
            
            # 如果计算结果不合理，使用简化公式
            if flow_area <= 0:
                flow_area = shell_diameter * baffle_spacing * 0.3  # 假设30%的流通面积
            
            return flow_area if flow_area > 0 else 0.1  # 返回默认值
        except Exception as e:
            print(f"计算壳侧流通面积失败: {e}")
            return 0.1  # 返回默认值
    
    def calculate_flow_rate(self, velocity, temperature, side, heat_exchanger=None):
        """根据流速、温度、侧别和管径计算流量
        
        参数:
            velocity: 流速 (m/s)
            temperature: 温度 (°C)
            side: 侧别 ('tube' 或 'shell')
            heat_exchanger: 换热器信息（可选）
        
        返回:
            flow_rate: 质量流量 (kg/s)
        """
        try:
            if velocity is None or velocity <= 0:
                return 0
            
            # 根据侧别确定计算方式
            area = None
            if heat_exchanger:
                if side and side.lower() == 'tube':
                    # tube侧：使用管内径计算截面积
                    d_i = heat_exchanger.get('d_i_original', 0.02)
                    area = np.pi * (d_i ** 2) / 4
                else:
                    # shell侧：使用等效直径和流通面积
                    # 方法1：使用等效直径计算（更准确）
                    De = self.calculate_shell_equivalent_diameter(heat_exchanger)
                    area = np.pi * (De ** 2) / 4
                    
                    # 方法2：使用流通面积（备选，如果方法1不合理）
                    if area <= 0 or area > 1.0:  # 如果面积不合理
                        area = self.calculate_shell_flow_area(heat_exchanger)
                        print(f"使用壳侧流通面积计算: {area:.6f} m²")
                    else:
                        print(f"使用壳侧等效直径计算: De={De:.6f} m, area={area:.6f} m²")
            
            if area is None or area <= 0:
                # 默认值：使用管内径
                d_i = 0.02
                area = np.pi * (d_i ** 2) / 4
                print(f"使用默认管径计算面积: {area:.6f} m²")
            
            # 获取流体密度（根据温度）
            if temperature is None or temperature <= 0:
                temperature = 25  # 默认25°C
            
            # 获取水的物性参数
            water_props = self.get_water_properties(temperature)
            density = water_props['rho']  # kg/m³
            
            # 计算质量流量: flow_rate = velocity * area * density (kg/s)
            flow_rate = velocity * area * density
            
            return flow_rate if flow_rate > 0 else 0
        except Exception as e:
            print(f"计算flow_rate失败: {e}")
            return 0
    
    def insert_operation_parameters(self, data, heat_exchanger=None):
        """将运行参数插入到生产数据库，遇到重复键时更新现有记录
        在插入前会计算并填充缺失的flow_rate值
        """
        if not data:
            return True
        
        # 处理数据：计算缺失的flow_rate
        processed_data = []
        for record in data:
            # 创建数据副本，避免修改原始数据
            processed_record = record.copy()
            
            # 如果flow_rate为None或0，尝试计算
            if processed_record.get('flow_rate') is None or processed_record.get('flow_rate') == 0:
                velocity = processed_record.get('velocity')
                temperature = processed_record.get('temperature')
                side = processed_record.get('side', 'tube')
                
                # 计算flow_rate
                if velocity is not None and velocity > 0 and temperature is not None and temperature > 0:
                    flow_rate = self.calculate_flow_rate(velocity, temperature, side, heat_exchanger)
                    processed_record['flow_rate'] = flow_rate
                    # 移除flow_rate计算结果的输出
                    if flow_rate <= 0:
                        # 如果计算结果为0，设置为一个很小的值避免NULL
                        processed_record['flow_rate'] = 0.0001
                else:
                    # 如果无法计算，设置为一个很小的值避免NULL
                    processed_record['flow_rate'] = 0.0001
                    # 移除velocity和temperature无效的警告输出
            
            # 确保所有可能为None的字段都有默认值
            if processed_record.get('flow_rate') is None:
                processed_record['flow_rate'] = 0
            if processed_record.get('velocity') is None:
                processed_record['velocity'] = 0
            
            processed_data.append(processed_record)
        
        # 构建插入语句，使用ON DUPLICATE KEY UPDATE避免重复键错误并更新数据
        columns = ', '.join(processed_data[0].keys())
        placeholders = ', '.join(['%s'] * len(processed_data[0]))
        # 构建ON DUPLICATE KEY UPDATE子句
        update_clause = ', '.join([f"{col} = VALUES({col})" for col in processed_data[0].keys()])
        query = f"INSERT INTO operation_parameters ({columns}) VALUES ({placeholders}) ON DUPLICATE KEY UPDATE {update_clause}"
        
        # 准备数据
        values = []
        for record in processed_data:
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
        """将物理参数插入到生产数据库，遇到重复键时更新现有记录"""
        if not data:
            return True
        
        # 构建插入语句，使用ON DUPLICATE KEY UPDATE避免重复键错误并更新数据
        columns = ', '.join(data[0].keys())
        placeholders = ', '.join(['%s'] * len(data[0]))
        # 构建ON DUPLICATE KEY UPDATE子句
        update_clause = ', '.join([f"{col} = VALUES({col})" for col in data[0].keys()])
        query = f"INSERT INTO physical_parameters ({columns}) VALUES ({placeholders}) ON DUPLICATE KEY UPDATE {update_clause}"
        
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
        # 计算时间范围，确保日期格式正确（day需要前导零）
        start_date = f"2022-01-{day:02d} {hour:02d}:00:00"
        end_date = f"2022-01-{day:02d} {hour:02d}:59:59"
        
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
        """将性能参数插入到生产数据库，遇到重复键时更新现有记录"""
        if not data:
            return True
        
        # 确保所有记录都有相同的字段
        # 获取第一个记录的字段
        fields = set(data[0].keys())
        
        # 过滤掉字段不一致的记录
        filtered_data = []
        for record in data:
            if set(record.keys()) == fields:
                filtered_data.append(record)
            else:
                # 打印不一致的字段信息以便调试
                print(f"过滤掉字段不一致的记录: {record}")
        
        if not filtered_data:
            print("没有有效的性能参数数据可以插入")
            return True
        
        # 构建插入语句，使用ON DUPLICATE KEY UPDATE避免重复键错误
        columns = ', '.join(filtered_data[0].keys())
        placeholders = ', '.join(['%s'] * len(filtered_data[0]))
        
        # 构建ON DUPLICATE KEY UPDATE子句
        update_clause = ', '.join([f"{col} = VALUES({col})" for col in filtered_data[0].keys()])
        query = f"INSERT INTO performance_parameters ({columns}) VALUES ({placeholders}) ON DUPLICATE KEY UPDATE {update_clause}"
        
        # 准备数据
        values = []
        for record in filtered_data:
            values.append(tuple(record.values()))
        
        try:
            # 批量插入或更新
            self.db_conn.prod_cursor.executemany(query, values)
            self.db_conn.commit(self.db_conn.prod_db)
            return True
        except Exception as e:
            print(f"插入/更新性能参数失败: {e}")
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
            if temperature is None or temperature <= 0:
                print(f"警告: 运行参数中的温度无效 (temperature={temperature})，使用默认值25°C")
                temperature = 25
            
            # 从pyfluids获取水的物性参数
            water_props = self.get_water_properties(temperature)
            
            # 从物理参数表获取导热系数
            key = (op_data['points'], op_data['side'])
            thermal_conductivity = physical_map.get(key, {}).get('thermal_conductivity', water_props['lambda'])
            if thermal_conductivity is None or thermal_conductivity <= 0:
                thermal_conductivity = water_props['lambda']
            
            # 获取流速
            velocity = op_data.get('velocity', 0)
            if velocity is None or velocity <= 0:
                velocity = 0
                if op_data.get('side') == 'shell':
                    op_data['velocity'] = 0  # 为壳侧流速设置默认值0
                # 只保留关键警告信息
                if op_data.get('side') != 'shell':  # 只对非壳侧打印警告
                    print(f"警告: 运行参数中的流速无效 (velocity={velocity})，points={op_data.get('points')}, side={op_data.get('side')}")
            
            # 计算雷诺数和普朗特数
            Re = self.calculate_reynolds_number(
                water_props['rho'], 
                velocity, 
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
        # 计算时间范围，确保日期格式正确（day需要前导零）
        start_date = f"2022-01-01 00:00:00"
        end_date = f"2022-01-{training_days:02d} 23:59:59"
        
        query = """
        SELECT p.*, k.K_LMTD AS K_lmtd
        FROM physical_parameters p
        LEFT JOIN k_management k ON p.heat_exchanger_id = k.heat_exchanger_id 
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
        # 计算时间范围，确保日期格式正确（day需要前导零）
        start_date = f"2022-01-{day:02d} {hour:02d}:00:00"
        end_date = f"2022-01-{day:02d} {hour:02d}:59:59"
        
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
        # 计算时间范围，确保日期格式正确（day需要前导零）
        start_date = f"2022-01-{day:02d} 00:00:00"
        end_date = f"2022-01-{day:02d} {optimization_hours-1:02d}:59:59"
        
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
    
    def get_optimization_data_for_stage2(self, day, optimization_hours, history_days):
        """获取阶段2优化数据，包括当天的optimization_hours和历史数据"""
        # 获取当天的optimization_hours数据
        day_start_date = f"2022-01-{day:02d} 00:00:00"
        day_end_date = f"2022-01-{day:02d} {optimization_hours-1:02d}:59:59"
        
        # 获取历史数据（history_days天）
        history_start_day = max(1, day - history_days)
        history_start_date = f"2022-01-{history_start_day:02d} 00:00:00"
        history_end_date = f"2022-01-{day-1:02d} 23:59:59"
        
        # 合并查询：当天的optimization_hours + 历史history_days天
        # 使用LEFT JOIN替代INNER JOIN，确保即使k_management表中没有对应记录，也能获取physical_parameters表的数据
        query = """
        SELECT p.*, k.K_actual
        FROM physical_parameters p
        LEFT JOIN k_management k ON p.heat_exchanger_id = k.heat_exchanger_id 
                           AND p.timestamp = k.timestamp 
                           AND p.points = k.points 
                           AND p.side = k.side
        WHERE (p.timestamp BETWEEN %s AND %s)
           OR (p.timestamp BETWEEN %s AND %s)
        """
        params = (day_start_date, day_end_date, history_start_date, history_end_date)
        
        if self.db_conn.execute_query(self.db_conn.prod_cursor, query, params):
            return self.db_conn.fetch_all(self.db_conn.prod_cursor)
        return []
    
    def get_data_for_reprocess(self, start_day, end_day):
        """获取指定天数范围内的数据，用于重新处理"""
        start_date = f"2022-01-{start_day:02d} 00:00:00"
        end_date = f"2022-01-{end_day:02d} 23:59:59"
        
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
    
    def calculate_average_error(self, day, hours=None):
        """计算指定天数的平均误差（K_predicted vs K_actual）"""
        if hours is None:
            start_date = f"2022-01-{day:02d} 00:00:00"
            end_date = f"2022-01-{day:02d} 23:59:59"
        else:
            start_date = f"2022-01-{day:02d} {hours[0]:02d}:00:00"
            end_date = f"2022-01-{day:02d} {hours[1]:02d}:59:59"
        
        query = """
        SELECT AVG(ABS(K_predicted - K_actual) / NULLIF(K_actual, 0) * 100) as avg_error
        FROM k_management
        WHERE timestamp BETWEEN %s AND %s
          AND K_actual > 0
          AND K_predicted > 0
        """
        params = (start_date, end_date)
        
        if self.db_conn.execute_query(self.db_conn.prod_cursor, query, params):
            result = self.db_conn.fetch_one(self.db_conn.prod_cursor)
            return result['avg_error'] if result and result['avg_error'] is not None else 0
        return 0
    
    def update_performance_parameters_k(self, data):
        """更新performance_parameters表的K字段"""
        if not data:
            return True
        
        # 构建更新语句
        query = """
        UPDATE performance_parameters 
        SET K = %s 
        WHERE heat_exchanger_id = %s AND timestamp = %s AND points = %s AND side = %s
        """
        
        # 准备数据
        values = []
        for record in data:
            values.append((
                record.get('K', 0),
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
            print(f"更新performance_parameters的K值失败: {e}")
            self.db_conn.rollback(self.db_conn.prod_db)
            return False
    






