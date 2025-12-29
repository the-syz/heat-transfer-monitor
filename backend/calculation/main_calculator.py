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
        # 加载配置
        with open(config_file, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        
        # 初始化数据库连接
        self.db_conn = DatabaseConnection(self.config)
        
        # 建立数据库连接
        test_db_result = self.db_conn.connect_test_db()
        prod_db_result = self.db_conn.connect_prod_db()
        
        print(f"测试数据库连接结果: {test_db_result}")
        print(f"生产数据库连接结果: {prod_db_result}")
        print(f"生产数据库连接状态: {self.db_conn.prod_db is not None}")
        print(f"生产数据库游标状态: {self.db_conn.prod_cursor is not None}")
        
        # 初始化数据加载器
        self.data_loader = DataLoader(self.db_conn)
        
        # 获取换热器信息
        self.heat_exchangers = self.data_loader.get_all_heat_exchangers()
        self.heat_exchanger = self.heat_exchangers[0] if self.heat_exchangers else {}
        self.geometry_params = self.heat_exchanger if self.heat_exchanger else {}
        
        # 初始化计算器
        self.lmtd_calc = LMTDCalculator()
        self.nonlinear_calc = NonlinearRegressionCalculator(self.geometry_params)
        
        # 初始化阶段标志
        self.stage = 1  # 1: 阶段1, 2: 阶段2
        self.training_days = self.config.get('training_days', 20)
        self.optimization_hours = self.config.get('optimization_hours', 3)
        self.history_days = self.config.get('history_days', 3)
        self.stage1_error_threshold = self.config.get('stage1_error_threshold', 5)
        self.stage1_history_days = self.config.get('stage1_history_days', 5)
        
        # 初始化模型参数
        self.model_params = None
        
        # 计算换热面积
        self.calculate_heat_exchanger_area()
        
        # 尝试从数据库加载已训练的模型参数
        try:
            # 查询最新的模型参数
            query = "SELECT a, p, b FROM model_parameters ORDER BY timestamp DESC LIMIT 1"
            self.db_conn.prod_cursor.execute(query)
            result = self.db_conn.prod_cursor.fetchone()
            
            if result:
                self.model_params = {
                    'a': result[0],
                    'p': result[1],
                    'b': result[2]
                }
                print(f"从数据库加载已训练的模型参数: a={self.model_params['a']:.6f}, p={self.model_params['p']:.6f}, b={self.model_params['b']:.6f}")
        except Exception as e:
            print(f"加载模型参数失败: {e}")
            self.model_params = None
        
        # 初始化训练数据
        self.training_data = []
        
        # 标记是否正在重新处理历史数据，避免无限循环
        self.reprocessing_history = False
        
        # 获取所有换热器ID
        self.heat_exchanger_ids = [1]  # 默认使用ID为1的换热器
        
        # 回调函数，用于通知stage1/stage2完成
        self.on_stage1_complete_callback = None
        self.on_stage2_complete_callback = None
        self.on_error_retrain_complete_callback = None
    
    def load_config(self):
        """加载配置文件"""
        with open(self.config_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def calculate_heat_exchanger_area(self):
        """计算换热面积"""
        # 优先使用数据库中已有的换热面积
        if self.heat_exchanger:
            if self.heat_exchanger.get('heat_exchange_area') is not None and self.heat_exchanger['heat_exchange_area'] > 0:
                self.heat_exchanger_area = self.heat_exchanger['heat_exchange_area']
                return
            
            # 如果数据库中没有换热面积，则根据换热器参数计算
            d_o = self.heat_exchanger['d_o']
            # 优先使用tube_count，如果没有则使用tube_section_count作为备选
            tube_count = self.heat_exchanger.get('tube_count') or self.heat_exchanger.get('tube_section_count', 0)
            # 从数据库读取管长，如果没有则使用默认值
            tube_length = self.heat_exchanger.get('tube_length', 9.0)  # 默认9米（根据数据库初始化数据）
            
            if tube_count > 0 and d_o > 0 and tube_length > 0:
                # 计算总面积：π * 管外径 * 管长 * 管数
                self.heat_exchanger_area = np.pi * d_o * tube_length * tube_count
            else:
                # 如果缺少必要参数，使用默认面积
                self.heat_exchanger_area = 188.0  # 默认188 m²（根据数据库初始化数据）
        else:
            # 如果没有换热器数据，使用默认面积
            self.heat_exchanger_area = 188.0
    
    def get_heat_exchanger_area(self):
        """获取换热面积"""
        return self.heat_exchanger_area
    
    def set_stage1_complete_callback(self, callback):
        """设置stage1完成时的回调函数"""
        self.on_stage1_complete_callback = callback
    
    def set_stage2_complete_callback(self, callback):
        """设置stage2完成时的回调函数"""
        self.on_stage2_complete_callback = callback
    
    def set_error_retrain_complete_callback(self, callback):
        """设置误差超限重新训练完成时的回调函数"""
        self.on_error_retrain_complete_callback = callback
    
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
            # 将side转换为大写，确保大小写一致
            side = data['side'].upper()
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
            # 检查热侧数据是否完整
            if hot_side in temp_data and 1 in temp_data[hot_side] and 2 in temp_data[hot_side]:
                T_h_in = temp_data[hot_side][1] or 0
                T_h_out = temp_data[hot_side][2] or 0
            else:
                T_h_in = 0
                T_h_out = 0
            
            # 获取冷侧温度
            # 检查冷侧数据是否完整
            if cold_side in temp_data and 1 in temp_data[cold_side] and 2 in temp_data[cold_side]:
                T_c_in = temp_data[cold_side][1] or 0
                T_c_out = temp_data[cold_side][2] or 0
            else:
                T_c_in = 0
                T_c_out = 0
            
            # 计算LMTD
            # 确保所有温度值都有效且大于0
            if T_h_in > 0 and T_h_out > 0 and T_c_in > 0 and T_c_out > 0:
                lmtd = self.lmtd_calc.calculate_lmtd(
                    T_h_in, T_h_out, T_c_in, T_c_out, flow_type='counterflow'
                )
                lmtd_map[timestamp] = lmtd
            else:
                # 只有当所有必要的温度值都存在且大于0时，才计算LMTD
                print(f"警告: 时间戳 {timestamp} 的温度数据不完整或无效，无法计算LMTD")
                print(f"热侧温度: T_h_in={T_h_in}, T_h_out={T_h_out}")
                print(f"冷侧温度: T_c_in={T_c_in}, T_c_out={T_c_out}")
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
        
        # 过滤tube侧数据，不区分大小写
        training_data = [data for data in training_data if data.get('side', '').lower() == 'tube']
        
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
        
        # 过滤tube侧数据，不区分大小写
        optimization_data = [data for data in optimization_data if data.get('side', '').lower() == 'tube']
        
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
            if record.get('side', '').lower() != 'tube':
                continue
            
            timestamp = record['timestamp']
            heat_exchanger_id = record['heat_exchanger_id']
            points = record['points']
            Re = record.get('reynolds', 0)
            
            if Re > 0 and self.model_params:
                # 预测K值
                K_pred = self.nonlinear_calc.predict_K(Re, self.model_params['a'], self.model_params['p'], self.model_params['b'])
                k_predicted_map[(heat_exchanger_id, timestamp, points)] = K_pred
                
                # 计算alpha_i
                alpha_i = 1 / (self.model_params['a'] * np.power(Re, -self.model_params['p']))
                alpha_i_map[(heat_exchanger_id, timestamp, points)] = alpha_i
        
        return k_predicted_map, alpha_i_map
    
    def process_data_by_hour(self, day, hour, discard_no_k=False):
        """处理指定天数和小时的数据，按照用户指定的8步流程执行
        
        参数:
            day: 天数
            hour: 小时
            discard_no_k: 是否弃用没有K值的数据（仅用于脚本）
        """
        # 步骤1: 读取运行参数全表（operation_parameters）
        operation_data = self.data_loader.get_operation_parameters_by_hour(day, hour)
        if not operation_data:
            print(f"第{day}天第{hour}小时没有运行参数数据")
            return False
        
        # 将运行参数插入到生产数据库（传入heat_exchanger用于计算flow_rate）
        if not self.data_loader.insert_operation_parameters(operation_data, self.heat_exchanger):
            print("插入运行参数失败")
            return False

        # 步骤2: 计算物理参数、雷诺数和普朗特数
        # 先尝试从测试数据库读取物理参数
        physical_data = self.data_loader.get_physical_parameters_by_hour(day, hour)
        
        # 计算物理参数（处理所有侧的数据）
        processed_data = self.data_loader.process_operation_data(operation_data, physical_data, self.heat_exchanger)
        
        # 过滤tube侧数据，不区分大小写，用于后续模型训练和K_predicted计算
        tube_processed_data = [data for data in processed_data if data.get('side', '').lower() == 'tube']

        # 步骤3: 读取测试数据库中的性能参数，填入k_management和performance_parameters
        test_performance_data = self.data_loader.get_test_performance_parameters_by_hour(day, hour)
        
        # 构建测试性能参数映射表
        test_performance_map = {}
        for data in test_performance_data:
            # 如果启用了弃用无K值数据的功能，并且K值为None或0，则跳过
            if discard_no_k and (data.get('K') is None or data.get('K') == 0):
                continue
            
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
        # print(f"温度映射表包含 {len(temp_map)} 个时间戳")
        
        # 构建热负荷映射表
        heat_duty_map = {}        
        # 先尝试从test_performance_data获取heat_duty
        for data in test_performance_data:
            heat_duty = data.get('heat_duty')  # 获取原始值，不设置默认值
            # 确保heat_duty是一个数值，如果为None或<=0，则计算
            if heat_duty is None or heat_duty <= 0:
                # 如果heat_duty为None、0或未定义，尝试计算
                heat_duty = self.calculate_heat_duty(data, processed_data, operation_data)
            heat_duty_map[data['timestamp']] = heat_duty
        # print(f"热负荷映射表包含 {len(heat_duty_map)} 个时间戳")
        
        # 计算LMTD
        lmtd_map = self.calculate_lmtd(operation_data)
        
        # 计算K_lmtd
        k_lmtd_map = self.calculate_k_lmtd(heat_duty_map, lmtd_map)
        
        # 只处理tube侧数据，用于构建k_management和performance_parameters
        for data in tube_processed_data:
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
                'lmtd': lmtd,  # 修复字段名：LMTD改为lmtd
                'alpha_o': alpha_o,
                'alpha_i': 0,  # 添加alpha_i字段，设置默认值0
                'heat_exchanger_id': heat_exchanger_id,
                'fouling_resistance': self.nonlinear_calc.calculate_fouling_resistance(day) if self.model_params else 0,
                'K': 0  # 添加K字段的默认值0
            }
            performance_data.append(performance_entry)
        
        # 将k_management数据插入到生产数据库
        if not self.data_loader.insert_k_management(k_management_data):
            print("插入K_management失败")
            return False
        
        # 步骤5: 阶段1训练（在training_days的所有数据读取完成后触发，即第training_days天的第23小时之后）
        if self.stage == 1 and not self.model_params and day == self.training_days and hour == 23:
            print(f"第{self.training_days}天的所有数据已读取完成，触发阶段1训练")
            self.train_stage1()
            self.stage = 2
            print("阶段1训练完成，开始重新处理之前所有天数的数据，以更新K_predicted和性能参数...")
            # 标记正在重新处理，避免无限循环
            self.reprocessing_history = True
            # 重新处理从第1天到当前天的数据
            for reprocess_day in range(1, day + 1):
                for reprocess_hour in range(24):
                    print(f"重新处理第{reprocess_day}天第{reprocess_hour}小时的数据...")
                    # 临时设置reprocessing标志，避免再次触发训练
                    old_reprocessing = self.reprocessing_history
                    self.reprocessing_history = True
                    self.process_data_by_hour(reprocess_day, reprocess_hour)
                    self.reprocessing_history = old_reprocessing
            self.reprocessing_history = False
            print("所有历史数据重新处理完成")
            # 调用stage1完成回调
            if self.on_stage1_complete_callback:
                self.on_stage1_complete_callback(day)
        
        # 步骤6: 计算K_predicted和alpha_i（仅在stage1训练完成后）
        # 初始化alpha_i_map和k_predicted_map，避免后续使用时出错
        alpha_i_map = {}
        k_predicted_map = {}
        # 只有在stage1训练完成后（有model_params）才计算K_predicted
        if self.model_params:
            k_predicted_map, alpha_i_map = self.predict_k_and_alpha_i(tube_processed_data)
            
            # 更新k_management数据，添加K_predicted
            for data in k_management_data:
                key = (data['heat_exchanger_id'], data['timestamp'], data['points'])
                data['K_predicted'] = k_predicted_map.get(key, 0)
            
            # 更新k_management表
            self.data_loader.update_k_management_with_predicted(k_management_data)
        else:
            # stage1训练之前，K_predicted设为0
            for data in k_management_data:
                data['K_predicted'] = 0
            # 将stage1训练之前的K_predicted=0更新到数据库
            self.data_loader.update_k_management_with_predicted(k_management_data)

        # 确保为所有performance_data添加alpha_i字段，即使没有model_params
        for data in performance_data:
            key = (data['heat_exchanger_id'], data['timestamp'], data['points'])
            data['alpha_i'] = alpha_i_map.get(key, 0)  # 默认为0，如果没有计算值
        
        # 构建k_key_map，用于步骤8中快速查找K_predicted
        k_key_map = {}
        if self.model_params and k_predicted_map:
            for data in tube_processed_data:
                k_key = (data['heat_exchanger_id'], data['timestamp'], data['points'])
                if k_key not in k_key_map:
                    k_key_map[k_key] = k_predicted_map.get(k_key, 0)
        
        # 步骤7: 阶段2优化（阶段1训练完成后，在optimization_hours之后进行）
        # 只有在完成阶段1训练后，才考虑阶段2训练
        if self.stage == 2 and not self.reprocessing_history:
            # 在optimization_hours之后执行阶段2训练（例如第3小时之后）
            if hour == self.optimization_hours:
                print(f"第{day}天已读取{self.optimization_hours}小时数据，触发阶段2优化")
                # 获取优化数据：当天的optimization_hours + 历史history_days天
                optimization_data = self.data_loader.get_optimization_data_for_stage2(
                    day, self.optimization_hours, self.history_days
                )
                if optimization_data:
                    # 执行阶段2训练
                    self.train_stage2(optimization_data)
                    print(f"阶段2优化完成，开始重新计算第{day}天所有小时的K_predicted...")
                    # 重新处理当天的所有小时，更新K_predicted
                    for reprocess_hour in range(24):
                        # 获取该小时的数据
                        hour_operation_data = self.data_loader.get_operation_parameters_by_hour(day, reprocess_hour)
                        if hour_operation_data:
                            hour_physical_data = self.data_loader.get_physical_parameters_by_hour(day, reprocess_hour)
                            hour_processed_data = self.data_loader.process_operation_data(
                                hour_operation_data, hour_physical_data, self.heat_exchanger
                            )
                            hour_tube_data = [d for d in hour_processed_data if d.get('side', '').lower() == 'tube']
                            if hour_tube_data:
                                # 重新计算K_predicted
                                hour_k_predicted_map, hour_alpha_i_map = self.predict_k_and_alpha_i(hour_tube_data)
                                # 更新k_management
                                hour_k_management = []
                                for d in hour_tube_data:
                                    key = (d['heat_exchanger_id'], d['timestamp'], d['points'])
                                    hour_k_management.append({
                                        'heat_exchanger_id': d['heat_exchanger_id'],
                                        'timestamp': d['timestamp'],
                                        'points': d['points'],
                                        'side': d['side'],
                                        'K_predicted': hour_k_predicted_map.get(key, 0)
                                    })
                                if hour_k_management:
                                    self.data_loader.update_k_management_with_predicted(hour_k_management)
                                
                                # 更新performance_parameters表的K值
                                hour_perf_update = []
                                for d in hour_tube_data:
                                    key = (d['heat_exchanger_id'], d['timestamp'], d['points'])
                                    K_predicted = hour_k_predicted_map.get(key, 0)
                                    if K_predicted > 0:
                                        hour_perf_update.append({
                                            'heat_exchanger_id': d['heat_exchanger_id'],
                                            'timestamp': d['timestamp'],
                                            'points': d['points'],
                                            'side': d['side'],
                                            'K': K_predicted
                                        })
                                if hour_perf_update:
                                    self.data_loader.update_performance_parameters_k(hour_perf_update)
                else:
                    print(f"第{day}天没有足够的优化数据，跳过阶段2训练")
                # 调用stage2完成回调
                if self.on_stage2_complete_callback:
                    self.on_stage2_complete_callback(day)
            
            # 检查误差，如果达到阈值，重新进入stage1
            if hour == 23 and day > self.training_days:
                avg_error = self.data_loader.calculate_average_error(day)
                print(f"第{day}天平均误差: {avg_error:.2f}%")
                if avg_error >= self.stage1_error_threshold:
                    print(f"误差达到阈值{self.stage1_error_threshold}%，重新进入阶段1训练")
                    self.stage = 1
                    self.model_params = None
                    # 重新训练stage1
                    self.train_stage1()
                    self.stage = 2
                    # 重新计算该天和stage1_history_days中的性能参数
                    reprocess_start_day = max(1, day - self.stage1_history_days)
                    print(f"重新处理第{reprocess_start_day}天到第{day}天的数据...")
                    self.reprocessing_history = True
                    for reprocess_day in range(reprocess_start_day, day + 1):
                        for reprocess_hour in range(24):
                            print(f"重新处理第{reprocess_day}天第{reprocess_hour}小时的数据...")
                            old_reprocessing = self.reprocessing_history
                            self.reprocessing_history = True
                            self.process_data_by_hour(reprocess_day, reprocess_hour)
                            self.reprocessing_history = old_reprocessing
                    self.reprocessing_history = False
                    print("重新训练后的数据重新处理完成")
                    # 调用误差超限重新训练完成回调
                    if self.on_error_retrain_complete_callback:
                        self.on_error_retrain_complete_callback(reprocess_start_day, day)
        
        # 步骤8: 填写performance_parameters中的K值
        for data in performance_data:
            # 获取K_actual和K_predicted
            key = (data['heat_exchanger_id'], data['timestamp'], data['points'], data['side'])
            K_actual = test_performance_map.get(key, {}).get('K_actual', 0)
            
            # 如果启用了弃用无K值数据的功能，并且K_actual为None或0，则跳过
            if discard_no_k and (K_actual is None or K_actual == 0):
                continue
            
            # 构建k_management查询键
            k_key = (data['heat_exchanger_id'], data['timestamp'], data['points'])
            # 确保k_predicted_map已初始化
            if self.model_params and k_key_map:
                K_predicted = k_key_map.get(k_key, 0)
            else:
                K_predicted = 0
            
            # 确保K值始终有一个有效的数值
            if self.reprocessing_history and self.model_params:
                data['K'] = K_predicted or 0
            # 阶段1优化中的所有K值按K_actual写
            elif self.stage == 1:
                data['K'] = K_actual or 0
            # 阶段2中optimization_hours前的K用K_actual，该天其他时间用K_predicted
            else:
                # 获取当前小时
                current_hour = hour
                if current_hour < self.optimization_hours:
                    data['K'] = K_actual or 0
                else:
                    data['K'] = K_predicted or 0
        
        # 检查performance_data中的数据
        if performance_data:
            sample_perf_data = performance_data[0]
            # print(f"准备插入的性能参数样本: K={sample_perf_data.get('K')}, heat_duty={sample_perf_data.get('heat_duty')}, "
            #       f"LMTD={sample_perf_data.get('LMTD')}, alpha_i={sample_perf_data.get('alpha_i')}, "
            #       f"alpha_o={sample_perf_data.get('alpha_o')}")
        
        # 将performance_parameters数据插入到生产数据库
        # 将performance_parameters数据插入到生产数据库
        # insert_performance_parameters使用ON DUPLICATE KEY UPDATE，会自动更新K值
        if not self.data_loader.insert_performance_parameters(performance_data):
            print("插入性能参数失败")
            return False
        
        print(f"第{day}天第{hour}小时的数据处理完成，共插入 {len(performance_data)} 条性能参数")
        return True
    
    def run_calculation(self, day, hour):
        """运行完整的计算流程"""
        # 处理数据
        if not self.process_data_by_hour(day, hour):
            return False
        
        return True
    
    def close(self):
        """关闭数据库连接"""
        self.db_conn.disconnect_test_db()
        self.db_conn.disconnect_prod_db()
    
    def __del__(self):
        """析构函数，关闭数据库连接"""
        self.close()

    def calculate_heat_duty(self, data, processed_data=None, operation_data=None):
        """计算热负荷
        参数:
            data: 包含流量、温度等信息的数据字典
            processed_data: 处理后的物理参数数据
            operation_data: 运行参数数据
        返回值:
            计算得到的热负荷值
        """
        try:
            # 获取流量、比热容和温度差
            flow_rate = data.get('flow_rate', 0)
            specific_heat = data.get('specific_heat', 4.1868)  # 默认水的比热容，单位：kJ/(kg·K)
            
            # 如果flow_rate为0，尝试从processed_data中获取
            if flow_rate <= 0 and processed_data:
                # 查找对应的处理后数据
                for p_data in processed_data:
                    if p_data['timestamp'] == data['timestamp'] and p_data['side'] == data['side']:
                        # 尝试从处理后数据中获取specific_heat
                        specific_heat = p_data.get('specific_heat', 4.1868)
                        # 查找对应的运行参数数据以获取velocity和temperature
                        if operation_data:
                            found_velocity = False
                            for op_data in operation_data:
                                if (op_data['timestamp'] == data['timestamp'] and 
                                    op_data['side'] == data['side'] and 
                                    op_data['points'] == p_data['points']):
                                    # 确保velocity是数值，即使为None也设置为0
                                    velocity = op_data.get('velocity', 0) or 0
                                    temperature = op_data.get('temperature', 0) or 0
                                    found_velocity = True
                                    # 如果是壳侧且流速仍然为0，直接设置为0（用户需求）
                                    if data['side'].lower() == 'shell':
                                        velocity = 0
                                        # logger.warning("壳侧没有流速数据，设置默认值为0")
                                    if velocity > 0:
                                        # 计算flow_rate
                                        flow_rate = self.data_loader.calculate_flow_rate(velocity, temperature, data['side'], self.heat_exchanger)
                                    break
                            # 如果没有找到对应的运行参数数据，且是壳侧，设置默认流速为0
                            if not found_velocity and data['side'].lower() == 'shell':
                                velocity = 0
                                temperature = 0
                                # logger.warning("壳侧没有找到运行参数数据，设置默认流速为0")
                        break
            
            # 获取温度信息，支持多种数据结构
            # 尝试直接获取温度差
            delta_T = data.get('delta_T', 0)
            
            if delta_T <= 0:
                # 如果没有温度差，尝试从温度点获取
                T_in = data.get('T_in', 0) or data.get('temperature_in', 0) or 0
                T_out = data.get('T_out', 0) or data.get('temperature_out', 0) or 0
                
                # 如果还没有温度，尝试从side特定的温度获取
                side = data.get('side', '').upper()
                if side == 'TUBE':
                    T_in = T_in or data.get('T_c_in', 0) or data.get('temperature_cold_in', 0) or 0
                    T_out = T_out or data.get('T_c_out', 0) or data.get('temperature_cold_out', 0) or 0
                else:
                    T_in = T_in or data.get('T_h_in', 0) or data.get('temperature_hot_in', 0) or 0
                    T_out = T_out or data.get('T_h_out', 0) or data.get('temperature_hot_out', 0) or 0
                
                # 如果仍然没有温度差，尝试从operation_data中获取
                if (T_in == 0 or T_out == 0) and operation_data:
                    # 按时间戳和侧别分组温度数据
                    temp_map = self.get_temperature_map(operation_data)
                    if data['timestamp'] in temp_map:
                        temp_data = temp_map[data['timestamp']]
                        # 获取热侧和冷侧
                        hot_side, cold_side = self.determine_hot_cold_sides()
                        
                        if side == 'TUBE':
                            # Tube侧是冷侧还是热侧？
                            if cold_side.lower() == 'tube':
                                T_in = temp_data.get(cold_side, {}).get(1, 0) or 0
                                T_out = temp_data.get(cold_side, {}).get(2, 0) or 0
                            elif hot_side.lower() == 'tube':
                                T_in = temp_data.get(hot_side, {}).get(1, 0) or 0
                                T_out = temp_data.get(hot_side, {}).get(2, 0) or 0
                        else:
                            # Shell侧
                            if cold_side.lower() == 'shell':
                                T_in = temp_data.get(cold_side, {}).get(1, 0) or 0
                                T_out = temp_data.get(cold_side, {}).get(2, 0) or 0
                            elif hot_side.lower() == 'shell':
                                T_in = temp_data.get(hot_side, {}).get(1, 0) or 0
                                T_out = temp_data.get(hot_side, {}).get(2, 0) or 0
                
                # 计算温度差
                delta_T = abs(T_out - T_in)
            
            # 确保所有参数都有效
            if flow_rate > 0 and delta_T > 0:
                # 热负荷计算公式：Q = m * c * ΔT
                # 注意：flow_rate的单位需要与specific_heat匹配
                heat_duty = flow_rate * specific_heat * delta_T
                return heat_duty
            else:
                # 如果当前侧的flow_rate为0，尝试使用另一侧的数据来计算heat_duty
                if flow_rate <= 0 and processed_data and operation_data:
                    # 获取另一侧的侧别
                    current_side = data['side'].lower()
                    other_side = 'tube' if current_side == 'shell' else 'shell'
                    
                    # 查找另一侧的处理后数据
                    for p_data in processed_data:
                        if p_data['timestamp'] == data['timestamp'] and p_data['side'].lower() == other_side:
                            # 尝试从处理后数据中获取specific_heat
                            other_specific_heat = p_data.get('specific_heat', 4.1868)
                            
                            # 查找另一侧的运行参数数据
                            for op_data in operation_data:
                                if (op_data['timestamp'] == data['timestamp'] and 
                                    op_data['side'].lower() == other_side and 
                                    op_data['points'] == p_data['points']):
                                    other_velocity = op_data.get('velocity', 0) or 0
                                    other_temperature = op_data.get('temperature', 0) or 0
                                    
                                    if other_velocity > 0:
                                        # 计算另一侧的flow_rate
                                        other_flow_rate = self.data_loader.calculate_flow_rate(other_velocity, other_temperature, other_side, self.heat_exchanger)
                                        
                                        # 获取另一侧的温度差
                                        other_temp_map = self.get_temperature_map(operation_data)
                                        if data['timestamp'] in other_temp_map:
                                            temp_data = other_temp_map[data['timestamp']]
                                            other_side_upper = other_side.upper()
                                            if other_side_upper in temp_data and 1 in temp_data[other_side_upper] and 2 in temp_data[other_side_upper]:
                                                other_T_in = temp_data[other_side_upper][1] or 0
                                                other_T_out = temp_data[other_side_upper][2] or 0
                                                other_delta_T = abs(other_T_out - other_T_in)
                                                
                                                if other_flow_rate > 0 and other_delta_T > 0:
                                                    # 使用另一侧的数据计算heat_duty
                                                    heat_duty = other_flow_rate * other_specific_heat * other_delta_T
                                                    # print(f"使用{other_side}侧的数据计算heat_duty: {heat_duty}")
                                                    return heat_duty
                                    break
                    
                # 检查哪个参数无效
                if flow_rate <= 0:
                    # print(f"警告: 流量参数无效 (flow_rate={flow_rate})")
                    pass
                if delta_T <= 0:
                    # print(f"警告: 温度差无效 (delta_T={delta_T})")
                    pass
                return 0
        except Exception as e:
            print(f"计算热负荷时发生错误: {e}")
            import traceback
            traceback.print_exc()  # 打印完整的错误堆栈
            return 0