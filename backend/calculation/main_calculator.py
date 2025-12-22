import json
import os
import numpy as np
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
        
        # 初始化阶段标志
        self.stage = 1  # 1: 阶段1, 2: 阶段2
        self.training_days = self.config.get('training_days', 20)
        self.optimization_hours = self.config.get('optimization_hours', 3)
        
        # 初始化模型参数
        self.model_params = None
        
        # 初始化训练数据
        self.training_data = []
        
        # 获取所有换热器ID
        self.heat_exchanger_ids = [he['id'] for he in heat_exchangers] if heat_exchangers else [1]
    
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
    
    def calculate_lmtd(self, operation_data):
        """计算LMTD值
        返回值: {timestamp: lmtd_value}
        """
        # 构建温度映射表
        temp_map = self.get_temperature_map(operation_data)
        
        # 确定热侧和冷侧
        hot_side, cold_side = self.determine_hot_cold_sides()
        
        # 计算每个时间戳的LMTD
        lmtd_map = {}
        for timestamp, temp_data in temp_map.items():
            # 获取热侧温度（假设points=1为入口，points=2为出口）
            T_h_in = temp_data.get(hot_side, {}).get(1, 0) or 0
            T_h_out = temp_data.get(hot_side, {}).get(2, 0) or 0
            
            # 获取冷侧温度
            T_c_in = temp_data.get(cold_side, {}).get(1, 0) or 0
            T_c_out = temp_data.get(cold_side, {}).get(2, 0) or 0
            
            # 计算LMTD
            # 确保所有温度值都不是None
            T_h_in = T_h_in or 0
            T_h_out = T_h_out or 0
            T_c_in = T_c_in or 0
            T_c_out = T_c_out or 0
            if T_h_in > 0 and T_h_out > 0 and T_c_in > 0 and T_c_out > 0:
                lmtd = self.lmtd_calc.calculate_lmtd(
                    T_h_in, T_h_out, T_c_in, T_c_out, flow_type='counterflow'
                )
                lmtd_map[timestamp] = lmtd
            else:
                lmtd_map[timestamp] = 0
        
        return lmtd_map
    
    def calculate_k_lmtd(self, heat_duty_map, lmtd_map):
        """计算K_lmtd值
        返回值: {timestamp: k_lmtd_value}
        """
        k_lmtd_map = {}
        heat_exchanger_area = self.get_heat_exchanger_area()
        
        for timestamp, Q in heat_duty_map.items():
            lmtd = lmtd_map.get(timestamp, 0)
            
            # 确保所有值都不是None
            Q = Q or 0
            lmtd = lmtd or 0
            heat_exchanger_area = heat_exchanger_area or 0
            
            if Q > 0 and lmtd > 0 and heat_exchanger_area > 0:
                k_lmtd = self.lmtd_calc.calculate_k_lmtd(Q, heat_exchanger_area, lmtd)
                k_lmtd_map[timestamp] = k_lmtd
            else:
                k_lmtd_map[timestamp] = 0
        
        return k_lmtd_map
    
    def train_stage1(self):
        """执行阶段1训练：使用training_days天的数据进行初始拟合"""
        print(f"开始阶段1训练，使用{self.training_days}天的数据...")
        
        # 获取阶段1训练数据
        training_data = self.data_loader.get_training_data_for_stage1(self.training_days)
        
        # 过滤tube侧数据
        training_data = [data for data in training_data if data['side'] == 'TUBE']
        
        if not training_data:
            print("阶段1训练数据为空")
            return None
        
        # 使用stage1进行初始拟合
        a, p, b = self.nonlinear_calc.get_optimized_parameters(
            training_data, 
            stage='stage1',
            adaptive_strategy='dynamic'
        )
        
        # 将训练得到的参数作为这些天的训练得到的参数
        self.model_params = {'a': a, 'p': p, 'b': b}
        
        # 将模型参数插入到model_parameters表
        self.data_loader.insert_model_parameters(self.model_params, stage='stage1')
        
        print(f"阶段1训练完成，参数: a={a:.6f}, p={p:.6f}, b={b:.6f}")
        return self.model_params
    
    def train_stage2(self, optimization_data):
        """执行阶段2训练：使用新数据进行优化"""
        print(f"开始阶段2训练，使用{len(optimization_data)}条数据...")
        
        # 过滤tube侧数据
        optimization_data = [data for data in optimization_data if data['side'] == 'TUBE']
        
        if not optimization_data:
            print("阶段2训练数据为空")
            return self.model_params
        
        # 使用stage2进行精确优化
        a_opt, p_opt, b_opt = self.nonlinear_calc.get_optimized_parameters(
            optimization_data, 
            initial_params=[self.model_params['a'], self.model_params['p'], self.model_params['b']],
            stage='stage2',
            adaptive_strategy='dynamic'
        )
        
        # 更新模型参数
        self.model_params = {'a': a_opt, 'p': p_opt, 'b': b_opt}
        
        # 将模型参数插入到model_parameters表
        self.data_loader.insert_model_parameters(self.model_params, stage='stage2')
        
        print(f"阶段2训练完成，参数: a={a_opt:.6f}, p={p_opt:.6f}, b={b_opt:.6f}")
        return self.model_params
    
    def predict_k_and_alpha_i(self, data):
        """预测K值和alpha_i值
        返回值: (k_predicted_map, alpha_i_map)
        """
        k_predicted_map = {}
        alpha_i_map = {}
        
        for record in data:
            if record['side'] != 'TUBE':
                continue
            
            timestamp = record['timestamp']
            points = record['points']
            heat_exchanger_id = record['heat_exchanger_id']
            Re = record.get('reynolds', 0)
            
            if Re > 0 and self.model_params:
                # 预测K值
                K_pred = self.nonlinear_calc.predict_K(Re, self.model_params['a'], self.model_params['p'], self.model_params['b'])
                k_predicted_map[(heat_exchanger_id, timestamp, points)] = K_pred
                
                # 计算alpha_i
                alpha_i = 1 / (self.model_params['a'] * np.power(Re, -self.model_params['p']))
                alpha_i_map[(heat_exchanger_id, timestamp, points)] = alpha_i
        
        return k_predicted_map, alpha_i_map
    
    def process_data_by_hour(self, day, hour):
        """处理指定天数和小时的数据，按照用户指定的8步流程执行"""
        print(f"处理第{day}天第{hour}小时的数据...")
        
        # 步骤1: 读取运行参数全表（operation_parameters）
        operation_data = self.data_loader.get_operation_parameters_by_hour(day, hour)
        if not operation_data:
            print(f"第{day}天第{hour}小时没有运行参数数据")
            return False
        
        # 将运行参数插入到生产数据库
        if not self.data_loader.insert_operation_parameters(operation_data):
            print("插入运行参数失败")
            return False
        
        # 步骤2: 计算物理参数、雷诺数和普朗特数
        # 先尝试从测试数据库读取物理参数
        physical_data = self.data_loader.get_physical_parameters_by_hour(day, hour)
        
        # 计算物理参数
        processed_data = self.data_loader.process_operation_data(operation_data, physical_data, self.heat_exchanger)
        
        # 过滤tube侧数据，不区分大小写
        processed_data = [data for data in processed_data if data.get('side', '').lower() == 'tube']
        
        if not processed_data:
            print(f"第{day}天第{hour}小时没有tube侧物理参数数据")
            return False
        
        # 将物理参数插入到生产数据库
        if not self.data_loader.insert_physical_parameters(processed_data):
            print("插入物理参数失败")
            return False
        
        # 步骤3: 读取测试数据库中的性能参数，填入k_management和performance_parameters
        test_performance_data = self.data_loader.get_test_performance_parameters_by_hour(day, hour)
        
        # 构建测试性能参数映射表
        test_performance_map = {}
        for data in test_performance_data:
            key = (data['heat_exchanger_id'], data['timestamp'], data['points'], data['side'])
            test_performance_map[key] = {
                'K_actual': data.get('K', 0),
                'alpha_o': data.get('alpha_o', 0)
            }
        
        # 构建k_management数据和performance_parameters数据
        k_management_data = []
        performance_data = []
        
        # 步骤4: 计算LMTD和K_lmtd
        # 构建温度映射表
        temp_map = self.get_temperature_map(operation_data)
        
        # 构建热负荷映射表
        heat_duty_map = {}
        for data in test_performance_data:
            heat_duty_map[data['timestamp']] = data.get('heat_duty', 0)
        
        # 计算LMTD
        lmtd_map = self.calculate_lmtd(operation_data)
        
        # 计算K_lmtd
        k_lmtd_map = self.calculate_k_lmtd(heat_duty_map, lmtd_map)
        
        for data in processed_data:
            timestamp = data['timestamp']
            heat_exchanger_id = data['heat_exchanger_id']
            points = data['points']
            side = data['side']
            
            # 获取测试数据库中的K_actual和alpha_o
            test_key = (heat_exchanger_id, timestamp, points, side)
            K_actual = test_performance_map.get(test_key, {}).get('K_actual', 0)
            alpha_o = test_performance_map.get(test_key, {}).get('alpha_o', 0)
            
            # 获取LMTD和K_lmtd
            lmtd = lmtd_map.get(timestamp, 0)
            K_lmtd = k_lmtd_map.get(timestamp, 0)
            
            # 构建k_management数据
            k_data = {
                'points': points,
                'side': side,
                'timestamp': timestamp,
                'K_actual': K_actual,
                'K_lmtd': K_lmtd,
                'heat_exchanger_id': heat_exchanger_id
            }
            k_management_data.append(k_data)
            
            # 构建performance_parameters数据
            performance_entry = {
                'points': points,
                'side': side,
                'timestamp': timestamp,
                'heat_duty': heat_duty_map.get(timestamp, 0),
                'LMTD': lmtd,
                'alpha_o': alpha_o,
                'heat_exchanger_id': heat_exchanger_id
            }
            performance_data.append(performance_entry)
        
        # 将k_management数据插入到生产数据库
        if not self.data_loader.insert_k_management(k_management_data):
            print("插入K_management失败")
            return False
        
        # 步骤5: 阶段1训练（当天数首次达到training_days参数值时触发）
        if self.stage == 1 and not self.model_params and day >= self.training_days:
            print(f"天数已达到{day}天，触发阶段1训练")
            self.train_stage1()
            self.stage = 2
        
        # 步骤6: 计算K_predicted和alpha_i
        # 初始化alpha_i_map，避免后续使用时出错
        alpha_i_map = {}
        if self.model_params:
            k_predicted_map, alpha_i_map = self.predict_k_and_alpha_i(processed_data)
            
            # 更新k_management数据，添加K_predicted
            for data in k_management_data:
                key = (data['heat_exchanger_id'], data['timestamp'], data['points'])
                data['K_predicted'] = k_predicted_map.get(key, 0)
            
            # 更新k_management表
            self.data_loader.update_k_management_with_predicted(k_management_data)
        
        # 确保为所有performance_data添加alpha_i字段，即使没有model_params
        for data in performance_data:
            key = (data['heat_exchanger_id'], data['timestamp'], data['points'])
            data['alpha_i'] = alpha_i_map.get(key, 0)  # 默认为0，如果没有计算值
        
        # 步骤7: 阶段2优化（阶段1训练完成后，以天为单位进行）
        # 只有在完成阶段1训练后，才考虑阶段2训练
        if self.stage == 2:
            # 每天只执行一次阶段2训练，在该天的最后一个小时（23点）执行
            if hour == 23:  # 假设每天24小时，最后一个小时是23点
                print(f"第{day}天结束，触发阶段2训练")
                # 获取当天的优化数据
                optimization_data = self.data_loader.get_optimization_data_for_stage2(day, 24)  # 使用全天24小时的数据
                if optimization_data:
                    # 执行阶段2训练
                    self.train_stage2(optimization_data)
                    # 重新计算K_predicted和alpha_i
                    k_predicted_map, alpha_i_map = self.predict_k_and_alpha_i(processed_data)
                    
                    # 更新k_management数据
                    for data in k_management_data:
                        key = (data['heat_exchanger_id'], data['timestamp'], data['points'])
                        data['K_predicted'] = k_predicted_map.get(key, 0)
                    
                    # 更新k_management表
                    self.data_loader.update_k_management_with_predicted(k_management_data)
                    
                    # 更新performance_parameters数据
                    for data in performance_data:
                        key = (data['heat_exchanger_id'], data['timestamp'], data['points'])
                        data['alpha_i'] = alpha_i_map.get(key, 0)
                else:
                    print(f"第{day}天没有足够的优化数据，跳过阶段2训练")
        
        # 步骤8: 填写performance_parameters中的K值
        for data in performance_data:
            # 获取K_actual和K_predicted
            key = (data['heat_exchanger_id'], data['timestamp'], data['points'], data['side'])
            K_actual = test_performance_map.get(key, {}).get('K_actual', 0)
            
            # 构建k_management查询键
            k_key = (data['heat_exchanger_id'], data['timestamp'], data['points'])
            K_predicted = k_predicted_map.get(k_key, 0) if self.model_params else 0
            
            # 阶段1优化中的所有K值按K_actual写
            if self.stage == 1:
                data['K'] = K_actual
            # 阶段2中optimization_hours前的K用K_actual，该天其他时间用K_predicted
            else:
                # 获取当前小时
                current_hour = hour
                if current_hour < self.optimization_hours:
                    data['K'] = K_actual
                else:
                    data['K'] = K_predicted
        
        # 将performance_parameters数据插入到生产数据库
        if not self.data_loader.insert_performance_parameters(performance_data):
            print("插入性能参数失败")
            return False
        
        print(f"第{day}天第{hour}小时的数据处理完成")
        return True
    
    def run_calculation(self, day, hour):
        """运行完整的计算流程"""
        # 处理数据
        if not self.process_data_by_hour(day, hour):
            return False
        
        return True
    
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
    
    def close(self):
        """关闭数据库连接"""
        self.db_conn.disconnect_test_db()
        self.db_conn.disconnect_prod_db()
    
    def __del__(self):
        """析构函数，关闭数据库连接"""
        self.close()