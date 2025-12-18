import json
import os
from datetime import datetime
import pandas as pd
from .lmtd_calculator import LMTDCalculator
from .nonlinear_regression import NonlinearRegressionCalculator
from db.data_loader import DataLoader
from db.db_connection import DatabaseConnection

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
            heat_exchanger = heat_exchangers[0]
            self.geometry_params = {
                'd_i_original': heat_exchanger['d_i_original'],
                'd_o': heat_exchanger['d_o'],
                'lambda_t': heat_exchanger['lambda_t']
            }
        else:
            # 如果没有数据，使用默认值
            self.geometry_params = {
                'd_i_original': 0.02,
                'd_o': 0.025,
                'lambda_t': 45.0
            }
        
        # 初始化计算器
        self.lmtd_calc = LMTDCalculator()
        self.nonlinear_calc = NonlinearRegressionCalculator(self.geometry_params)
    
    def load_config(self):
        """加载配置文件"""
        with open(self.config_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def process_data_by_hour(self, day, hour):
        """处理指定天数和小时的数据"""
        print(f"处理第{day}天第{hour}小时的数据...")
        
        # 从测试数据库读取运行参数
        operation_data = self.data_loader.get_operation_parameters_by_hour(day, hour)
        if not operation_data:
            print(f"第{day}天第{hour}小时没有运行参数数据")
            return False
        
        # 从测试数据库读取物理参数
        physical_data = self.data_loader.get_physical_parameters_by_hour(day, hour)
        if not physical_data:
            print(f"第{day}天第{hour}小时没有物理参数数据")
            return False
        
        # 处理运行数据，计算物理参数
        heat_exchangers = self.data_loader.get_all_heat_exchangers()
        heat_exchanger = heat_exchangers[0] if heat_exchangers else None
        processed_data = self.data_loader.process_operation_data(operation_data, physical_data, heat_exchanger)
        
        # 将运行参数插入到生产数据库
        if not self.data_loader.insert_operation_parameters(operation_data):
            print("插入运行参数失败")
            return False
        
        # 将物理参数插入到生产数据库
        if not self.data_loader.insert_physical_parameters(processed_data):
            print("插入物理参数失败")
            return False
        
        # 从测试数据库读取性能参数
        performance_data = self.data_loader.get_performance_parameters_by_hour(day, hour)
        if not performance_data:
            print(f"第{day}天第{hour}小时没有性能参数数据")
            return False
        
        # 将性能参数插入到生产数据库
        if not self.data_loader.insert_performance_parameters(performance_data):
            print("插入性能参数失败")
            return False
        
        # 创建performance_data的映射，方便快速查找
        performance_map = {(d['points'], d['side'], d['timestamp']): d for d in performance_data}
        
        # 计算K_lmtd
        k_management_data = []
        for data in processed_data:
            # 获取当前数据的关键信息
            points = data['points']
            side = data['side']
            timestamp = data['timestamp']
            
            # 从performance_data中查找对应的传热量Q
            key = (points, side, timestamp)
            performance = performance_map.get(key, {})
            Q = performance.get('heat_duty', 0)  # 从数据库获取传热量
            
            # 假设换热面积为1.0 m²（后续可从数据库获取或统一计算）
            heat_exchanger_area = 1.0
            
            # 根据side和points确定温度参数
            # 这里需要根据实际情况调整，假设：
            # - side='TUBE' 表示管侧，side='SHELL' 表示壳侧
            # - points=1 表示入口，points=2 表示出口
            # 实际应用中需要根据具体的points定义进行调整
            
            # 查找冷热流体的进出口温度
            # 这里需要根据实际的points和side定义来实现温度匹配逻辑
            # 以下是简化实现，实际应用中需要更复杂的逻辑
            
            # 假设points=1为入口，points=2为出口
            # 查找热侧（假设为管侧）的进出口温度
            T_h_in_key = (1, 'TUBE', timestamp) if side == 'TUBE' else (1, 'TUBE', timestamp)
            T_h_out_key = (2, 'TUBE', timestamp) if side == 'TUBE' else (2, 'TUBE', timestamp)
            # 查找冷侧（假设为壳侧）的进出口温度
            T_c_in_key = (1, 'SHELL', timestamp) if side == 'SHELL' else (1, 'SHELL', timestamp)
            T_c_out_key = (2, 'SHELL', timestamp) if side == 'SHELL' else (2, 'SHELL', timestamp)
            
            # 获取对应的温度数据
            T_h_in_data = performance_map.get(T_h_in_key, {})
            T_h_out_data = performance_map.get(T_h_out_key, {})
            T_c_in_data = performance_map.get(T_c_in_key, {})
            T_c_out_data = performance_map.get(T_c_out_key, {})
            
            # 获取温度值
            T_h_in = T_h_in_data.get('T_h_in', data.get('temperature', 0))
            T_h_out = T_h_out_data.get('T_h_out', data.get('temperature', 0))
            T_c_in = T_c_in_data.get('T_c_in', data.get('temperature', 0))
            T_c_out = T_c_out_data.get('T_c_out', data.get('temperature', 0))
            
            # 计算LMTD
            lmtd = self.lmtd_calc.calculate_lmtd(
                T_h_in,  # 热流体入口温度
                T_h_out,  # 热流体出口温度
                T_c_in,  # 冷流体入口温度
                T_c_out,  # 冷流体出口温度
                flow_type='counterflow'
            )
            
            # 计算K_lmtd
            k_lmtd = self.lmtd_calc.calculate_k_lmtd(Q, heat_exchanger_area, lmtd)
            
            # 构建K_management数据
            k_data = {
                'points': data['points'],
                'side': data['side'],
                'day': day,
                'hour': hour,
                'timestamp': data['timestamp'],
                'K_lmtd': k_lmtd,
                'heat_exchanger_id': data['heat_exchanger_id']
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