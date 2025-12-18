import json
import os
import numpy as np
from datetime import datetime
import pandas as pd
from .lmtd_calculator import LMTDCalculator
from .nonlinear_regression import NonlinearRegressionCalculator
from ..db.data_loader import DataLoader
from ..db.db_connection import DatabaseConnection

class MainCalculator:
    def __init__(self, config_file):
        self.config_file = config_file
        self.config = self.load_config()
        
        # 初始化数据库连接
        self.db_conn = DatabaseConnection(config_file)
        
        # 初始化数据加载器
        self.data_loader = DataLoader(self.db_conn)
        
        # 连接数据库
        self.db_conn.connect_test_db()
        self.db_conn.connect_prod_db()
        
        # 获取换热器信息
        heat_exchangers = self.data_loader.get_all_heat_exchangers()
        if heat_exchangers:
            # 假设使用第一个换热器的参数
            self.heat_exchanger = heat_exchangers[0]
            self.geometry_params = {
                'd_i_original': self.heat_exchanger['d_i_original'],
                'd_o': self.heat_exchanger['d_o'],
                'lambda_t': self.heat_exchanger['lambda_t'],
                'tube_side_fluid': self.heat_exchanger['tube_side_fluid'],
                'shell_side_fluid': self.heat_exchanger['shell_side_fluid']
            }
            # 计算换热面积（这里假设简单计算，后续可以考虑从数据库获取）
            self.calculate_heat_exchanger_area()
        else:
            # 如果没有数据，使用默认值
            self.heat_exchanger = None
            self.geometry_params = {
                'd_i_original': 0.02,
                'd_o': 0.025,
                'lambda_t': 45.0,
                'tube_side_fluid': '水',
                'shell_side_fluid': '轻柴油'
            }
            # 默认换热面积
            self.heat_exchanger_area = 1.0
        
        # 初始化计算器
        self.lmtd_calc = LMTDCalculator()
        self.nonlinear_calc = NonlinearRegressionCalculator(self.geometry_params)
    
    def load_config(self):
        """加载配置文件"""
        with open(self.config_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def calculate_heat_exchanger_area(self):
        """计算换热面积"""
        # 从换热器参数计算换热面积
        # 假设：d_o是管外径，tube_section_count是管数
        if self.heat_exchanger:
            d_o = self.heat_exchanger['d_o']
            tube_count = self.heat_exchanger['tube_section_count']
            # 假设管长为4米（可以根据实际情况调整）
            tube_length = 4.0
            # 计算总面积
            self.heat_exchanger_area = np.pi * d_o * tube_length * tube_count
        else:
            # 默认面积
            self.heat_exchanger_area = 1.0
    
    def get_heat_exchanger_area(self):
        """获取换热面积"""
        return self.heat_exchanger_area
    
    def determine_hot_cold_sides(self):
        """确定热侧和冷侧
        返回值: (hot_side, cold_side)
        """
        # 根据工质类型确定热侧和冷侧
        # 这里简单假设轻柴油为热侧，水为冷侧
        # 实际应用中可能需要更复杂的逻辑
        tube_fluid = self.geometry_params['tube_side_fluid']
        shell_fluid = self.geometry_params['shell_side_fluid']
        
        if '柴油' in shell_fluid:
            return ('SHELL', 'TUBE')
        elif '水' in shell_fluid:
            return ('TUBE', 'SHELL')
        else:
            # 默认假设管侧为热侧
            return ('TUBE', 'SHELL')
    
    def get_temperature_map(self, operation_data):
        """构建温度映射表，便于快速查找
        返回值: {timestamp: {side: {points: temperature}}}
        """
        temp_map = {}
        
        for data in operation_data:
            timestamp = data['timestamp']
            side = data['side']
            points = data['points']
            temperature = data['temperature']
            
            if timestamp not in temp_map:
                temp_map[timestamp] = {}
            if side not in temp_map[timestamp]:
                temp_map[timestamp][side] = {}
            temp_map[timestamp][side][points] = temperature
        
        return temp_map
    
    def process_data_by_hour(self, day, hour):
        """处理指定天数和小时的数据"""
        print(f"处理第{day}天第{hour}小时的数据...")
        
        # 从测试数据库读取运行参数
        operation_data = self.data_loader.get_operation_parameters_by_hour(day, hour)
        if not operation_data:
            print(f"第{day}天第{hour}小时没有运行参数数据")
            # 模拟生成一些测试数据
            # 注意：这里只是为了测试接口，实际应用中应该从数据库读取数据
            operation_data = [{
                'points': 1,
                'side': 'TUBE',
                'day': day,
                'hour': hour,
                'timestamp': f"2022-01-{day} {hour}:00:00",
                'temperature': 80,
                'flow_rate': 1.0,
                'pressure': 1.0,
                'velocity': 1.0,
                'heat_exchanger_id': 1
            }, {
                'points': 2,
                'side': 'TUBE',
                'day': day,
                'hour': hour,
                'timestamp': f"2022-01-{day} {hour}:00:00",
                'temperature': 60,
                'flow_rate': 1.0,
                'pressure': 1.0,
                'velocity': 1.0,
                'heat_exchanger_id': 1
            }, {
                'points': 1,
                'side': 'SHELL',
                'day': day,
                'hour': hour,
                'timestamp': f"2022-01-{day} {hour}:00:00",
                'temperature': 40,
                'flow_rate': 1.0,
                'pressure': 1.0,
                'velocity': 1.0,
                'heat_exchanger_id': 1
            }, {
                'points': 2,
                'side': 'SHELL',
                'day': day,
                'hour': hour,
                'timestamp': f"2022-01-{day} {hour}:00:00",
                'temperature': 30,
                'flow_rate': 1.0,
                'pressure': 1.0,
                'velocity': 1.0,
                'heat_exchanger_id': 1
            }]
        
        # 从测试数据库读取物理参数
        physical_data = self.data_loader.get_physical_parameters_by_hour(day, hour)
        if not physical_data:
            print(f"第{day}天第{hour}小时没有物理参数数据")
            # 模拟生成一些测试数据
            physical_data = [{
                'points': 1,
                'side': 'TUBE',
                'thermal_conductivity': 0.6,
                'dynamic_viscosity': 0.001,
                'specific_heat': 4186,
                'density': 1000,
                'prandtl_number': 7.0,
                'day': day,
                'hour': hour,
                'timestamp': f"2022-01-{day} {hour}:00:00",
                'heat_exchanger_id': 1
            }, {
                'points': 2,
                'side': 'TUBE',
                'thermal_conductivity': 0.6,
                'dynamic_viscosity': 0.001,
                'specific_heat': 4186,
                'density': 1000,
                'prandtl_number': 7.0,
                'day': day,
                'hour': hour,
                'timestamp': f"2022-01-{day} {hour}:00:00",
                'heat_exchanger_id': 1
            }, {
                'points': 1,
                'side': 'SHELL',
                'thermal_conductivity': 0.6,
                'dynamic_viscosity': 0.001,
                'specific_heat': 4186,
                'density': 1000,
                'prandtl_number': 7.0,
                'day': day,
                'hour': hour,
                'timestamp': f"2022-01-{day} {hour}:00:00",
                'heat_exchanger_id': 1
            }, {
                'points': 2,
                'side': 'SHELL',
                'thermal_conductivity': 0.6,
                'dynamic_viscosity': 0.001,
                'specific_heat': 4186,
                'density': 1000,
                'prandtl_number': 7.0,
                'day': day,
                'hour': hour,
                'timestamp': f"2022-01-{day} {hour}:00:00",
                'heat_exchanger_id': 1
            }]
        
        # 从测试数据库读取性能参数
        performance_data = self.data_loader.get_performance_parameters_by_hour(day, hour)
        if not performance_data:
            print(f"第{day}天第{hour}小时没有性能参数数据")
            # 模拟生成一些测试数据
            performance_data = [{
                'points': 1,
                'side': 'TUBE',
                'day': day,
                'hour': hour,
                'timestamp': f"2022-01-{day} {hour}:00:00",
                'heat_duty': 10000,
                'heat_exchanger_id': 1
            }, {
                'points': 2,
                'side': 'TUBE',
                'day': day,
                'hour': hour,
                'timestamp': f"2022-01-{day} {hour}:00:00",
                'heat_duty': 10000,
                'heat_exchanger_id': 1
            }, {
                'points': 1,
                'side': 'SHELL',
                'day': day,
                'hour': hour,
                'timestamp': f"2022-01-{day} {hour}:00:00",
                'heat_duty': 10000,
                'heat_exchanger_id': 1
            }, {
                'points': 2,
                'side': 'SHELL',
                'day': day,
                'hour': hour,
                'timestamp': f"2022-01-{day} {hour}:00:00",
                'heat_duty': 10000,
                'heat_exchanger_id': 1
            }]
        
        # 处理运行数据，计算物理参数
        processed_data = self.data_loader.process_operation_data(operation_data, physical_data, self.heat_exchanger)
        
        # 将运行参数插入到生产数据库
        if not self.data_loader.insert_operation_parameters(operation_data):
            print("插入运行参数失败")
            return False
        
        # 将物理参数插入到生产数据库
        if not self.data_loader.insert_physical_parameters(processed_data):
            print("插入物理参数失败")
            return False
        
        # 将性能参数插入到生产数据库
        if not self.data_loader.insert_performance_parameters(performance_data):
            print("插入性能参数失败")
            return False
        
        # 构建温度映射表
        temp_map = self.get_temperature_map(operation_data)
        
        # 构建性能参数映射表
        performance_map = {}
        for data in performance_data:
            timestamp = data['timestamp']
            if timestamp not in performance_map:
                performance_map[timestamp] = {
                    'heat_duty': data.get('heat_duty', 0)
                }
        
        # 确定热侧和冷侧
        hot_side, cold_side = self.determine_hot_cold_sides()
        
        # 计算每个时间戳的LMTD
        lmtd_map = {}
        for timestamp, temp_data in temp_map.items():
            # 获取热侧温度（假设points=1为入口，points=2为出口）
            T_h_in = temp_data.get(hot_side, {}).get(1, 0)
            T_h_out = temp_data.get(hot_side, {}).get(2, 0)
            
            # 获取冷侧温度
            T_c_in = temp_data.get(cold_side, {}).get(1, 0)
            T_c_out = temp_data.get(cold_side, {}).get(2, 0)
            
            # 计算LMTD
            if T_h_in > 0 and T_h_out > 0 and T_c_in > 0 and T_c_out > 0:
                lmtd = self.lmtd_calc.calculate_lmtd(
                    T_h_in, T_h_out, T_c_in, T_c_out, flow_type='counterflow'
                )
                lmtd_map[timestamp] = lmtd
            else:
                lmtd_map[timestamp] = 0
        
        # 计算K_lmtd
        k_management_data = []
        for data in processed_data:
            timestamp = data['timestamp']
            heat_exchanger_id = data['heat_exchanger_id']
            
            # 获取传热量Q
            Q = performance_map.get(timestamp, {}).get('heat_duty', 0)
            
            # 获取LMTD
            lmtd = lmtd_map.get(timestamp, 0)
            
            # 获取换热面积
            heat_exchanger_area = self.get_heat_exchanger_area()
            
            # 计算K_lmtd
            k_lmtd = 0
            if Q > 0 and lmtd > 0 and heat_exchanger_area > 0:
                k_lmtd = self.lmtd_calc.calculate_k_lmtd(Q, heat_exchanger_area, lmtd)
            
            # 构建K_management数据
            k_data = {
                'points': data['points'],
                'side': data['side'],
                'day': day,
                'hour': hour,
                'timestamp': timestamp,
                'K_lmtd': k_lmtd,
                'heat_exchanger_id': heat_exchanger_id
            }
            k_management_data.append(k_data)
        
        # 将K_lmtd插入到生产数据库
        if not self.data_loader.insert_k_management(k_management_data):
            print("插入K_management失败")
            return False
        
        print(f"第{day}天第{hour}小时的数据处理完成")
        return True
    
    def train_model(self, training_data):
        """训练非线性回归模型"""
        print("开始训练非线性回归模型...")
        
        # 使用stage1进行初始拟合
        a, p, b = self.nonlinear_calc.get_optimized_parameters(
            training_data, 
            stage='stage1',
            adaptive_strategy='dynamic'
        )
        
        # 使用stage2进行精确优化
        a_opt, p_opt, b_opt = self.nonlinear_calc.get_optimized_parameters(
            training_data, 
            initial_params=[a, p, b],
            stage='stage2',
            adaptive_strategy='dynamic'
        )
        
        print(f"模型训练完成，参数: a={a_opt:.6f}, p={p_opt:.6f}, b={b_opt:.6f}")
        return {'a': a_opt, 'p': p_opt, 'b': b_opt}
    
    def predict_performance(self, data, model_params):
        """预测换热器性能"""
        results = []
        
        for record in data:
            # 获取模型参数
            a = model_params['a']
            p = model_params['p']
            b = model_params['b']
            
            # 预测K值
            K_pred = self.nonlinear_calc.predict_K(record['reynolds_number'], a, p, b)
            
            # 计算alpha_i
            alpha_i = self.nonlinear_calc.calculate_alpha_i(a, p, record['reynolds_number'])
            
            # 计算alpha_o
            alpha_o = self.nonlinear_calc.calculate_alpha_o(record)
            
            # 计算结垢热阻
            fouling_resistance = self.nonlinear_calc.calculate_fouling_resistance(record['day'])
            
            # 构建结果
            result = {
                'points': record['points'],
                'side': record['side'],
                'day': record['day'],
                'hour': record['hour'],
                'timestamp': record['timestamp'],
                'K_predicted': K_pred,
                'alpha_i': alpha_i,
                'alpha_o': alpha_o,
                'fouling_resistance': fouling_resistance,
                'heat_exchanger_id': record.get('heat_exchanger_id', 1)
            }
            
            results.append(result)
        
        return results
    
    def run_calculation(self, day, hour):
        """运行完整的计算流程"""
        # 处理数据
        if not self.process_data_by_hour(day, hour):
            return False
        
        # 训练模型（这里简化处理，实际应该使用历史数据训练）
        # training_data = self.get_training_data(day, hour)
        # model_params = self.train_model(training_data)
        
        # 预测性能
        # prediction_data = self.get_prediction_data(day, hour)
        # predictions = self.predict_performance(prediction_data, model_params)
        
        return True
    
    def close(self):
        """关闭数据库连接"""
        self.db_conn.disconnect_test_db()
        self.db_conn.disconnect_prod_db()
    
    def __del__(self):
        """析构函数，关闭数据库连接"""
        self.close()