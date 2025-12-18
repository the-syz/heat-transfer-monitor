import numpy as np
import pandas as pd
from scipy.optimize import minimize
from datetime import datetime

class NonlinearRegressionCalculator:
    """
    基于非线性回归的热交换器传热系数优化计算器
    实现Y = a x^(-p) + b模型（其中Y=1/K，x=Re）的参数拟合
    """
    def __init__(self, geometry_params):
        self.geometry = geometry_params
        # 如果没有提供换热面积A，尝试根据其他参数计算
        if 'A' not in self.geometry:
            self.calculate_heat_exchanger_area()
    
    def calculate_heat_exchanger_area(self):
        """根据换热器参数计算换热面积
        与MainCalculator中的方法保持一致
        """
        d_o = self.geometry.get('d_o', 0.025)
        tube_count = self.geometry.get('tube_section_count', 100)  # 默认100根管子
        tube_length = 4.0  # 假设管长为4米
        
        # 计算总面积
        self.geometry['A'] = np.pi * d_o * tube_length * tube_count
    
    def model_func(self, x, a, p, b):
        """改进的模型函数：Y = a * x^(-p) + b
        增加数值稳定性处理
        """
        try:
            # 使用安全的幂运算，避免数值溢出
            x_safe = np.maximum(x, 1e-10)  # 确保x为正数
            power_term = np.power(x_safe, -p)
            
            # 添加数值稳定性处理
            if np.any(np.isinf(power_term)) or np.any(np.isnan(power_term)):
                # 对于极端情况，使用对数空间计算
                log_power = -p * np.log(x_safe)
                power_term = np.exp(np.minimum(log_power, 700))  # 避免exp溢出
            
            result = a * power_term + b
            
            # 确保结果有效
            result = np.maximum(result, 1e-10)  # 避免负结果或零
            
            return result
        except Exception as e:
            print(f"模型计算错误: {e}")
            return np.ones_like(x) * 1e-10
    
    def loss_func(self, params, x_data, y_data):
        """改进的损失函数：结合R²优化目标和相对误差"""
        a, p, b = params
        # 确保参数在合理范围内
        if a <= 0 or p <= 0 or b < 0:
            return 1e10  # 惩罚无效参数
        
        y_pred = self.model_func(x_data, a, p, b)
        # 避免除零错误
        valid_mask = y_pred > 0
        if not np.any(valid_mask):
            return 1e10
        
        # 使用有效数据
        y_actual_valid = y_data[valid_mask]
        y_pred_valid = y_pred[valid_mask]
        
        # 计算R²相关的损失（1-R²），直接优化决定系数
        ss_res = np.sum(np.square(y_actual_valid - y_pred_valid))
        y_mean = np.mean(y_actual_valid)
        ss_tot = np.sum(np.square(y_actual_valid - y_mean))
        
        # 避免除以零
        if ss_tot == 0:
            r2_loss = 0
        else:
            r2_loss = ss_res / ss_tot  # 1-R²
        
        # 计算相对误差平方和，保持对相对误差的控制
        relative_error = np.sum(np.square((y_actual_valid - y_pred_valid) / y_actual_valid))
        
        # 平衡R²优化和相对误差控制，根据数据尺度调整权重
        # 使用数据量归一化相对误差
        n = len(y_actual_valid)
        if n > 0:
            relative_error_normalized = relative_error / n
        else:
            relative_error_normalized = 0
        
        # 组合损失：主要优化R²，同时控制相对误差
        combined_loss = 0.7 * r2_loss + 0.3 * relative_error_normalized
        
        return combined_loss
    
    def prepare_data(self, experimental_data):
        """准备拟合数据，计算Re和Y=1/K，并进行数据清洗和标准化"""
        # 检查并转换数据格式
        if isinstance(experimental_data, pd.DataFrame):
            data_list = experimental_data.to_dict('records')
        else:
            data_list = experimental_data
        
        all_re = []
        all_y = []
        
        # 获取换热器参数
        A = self.geometry.get('A', 1.0)  # 换热面积 m²
        d_i = self.geometry.get('d_i_original', 0.02)  # 管内径 m
        A_cs = np.pi * (d_i ** 2) / 4  # 流通面积 m²
        
        for record in data_list:
            try:
                # 计算雷诺数Re
                if 'reynolds_number' in record and record['reynolds_number'] > 0:
                    Re = record['reynolds_number']
                elif 'Re' in record and record['Re'] > 0:
                    Re = record['Re']
                else:
                    # 计算Re
                    rho = record.get('density', 1000)  # 密度 kg/m³
                    u = record.get('velocity', 0)  # 流速 m/s
                    mu = record.get('dynamic_viscosity', 0.001)  # 粘度 Pa·s
                    
                    if u <= 0 or mu <= 0 or rho <= 0:
                        continue
                    
                    Re = rho * u * d_i / mu
                    
                    if Re <= 0 or Re > 1e6:  # 增加上限过滤异常值
                        continue
                
                # 计算Y=1/K
                if 'K_lmtd' in record and record['K_lmtd'] > 0:
                    K = record['K_lmtd']
                elif 'K' in record and record['K'] > 0:
                    K = record['K']
                else:
                    # 尝试从其他参数计算K
                    continue
                
                y = 1 / K
                
                # 过滤异常值（基于经验范围）
                if y < 0.0001 or y > 0.01:
                    continue
                
                # 存储数据
                all_re.append(Re)
                all_y.append(y)
                
            except Exception as e:
                continue
        
        return np.array(all_re), np.array(all_y)
    
    def get_optimized_parameters(self, experimental_data, initial_params=None, stage='default', adaptive_strategy='dynamic', max_error_threshold=0.15):
        """
        获取优化后的参数
        参数:
            experimental_data: 实验数据
            initial_params: 初始参数 [a, p, b]
            stage: 优化阶段，'stage1'或'stage2'或'default'
        返回:
            a_opt: 优化后的a值
            p_opt: 优化后的p值
            b_opt: 优化后的b值
        """
        print(f"获取{stage}阶段非线性回归参数...")
        
        # 准备数据
        x_data, y_data = self.prepare_data(experimental_data)
        
        if len(x_data) < 3:
            print("警告: 有效数据点不足，使用默认参数")
            # 返回合理的默认参数
            if stage == 'stage1':
                return 1.0, 0.85, 0.0004  # stage1使用更合理的默认值，b基于物理意义
            else:
                return 1.0, 0.8, 0.0004  # b基于物理意义设置为0.0004
        
        # 设置初始猜测值
        if initial_params is None:
            # 使用更合理的初始猜测值，基于实际物理意义和历史数据
            initial_guess = [0.5, 0.6, 0.0003]  # 更接近实际可能的参数范围
        else:
            initial_guess = initial_params
        
        # 根据阶段和自适应策略调整优化策略
        if stage == 'stage1':
            # stage1: 初始拟合，使用更合理的参数范围
            if adaptive_strategy == 'conservative':
                bounds = [(1e-6, 20), (0.4, 0.9), (0.0001, 0.0006)]  # 缩小范围以提高精度
            elif adaptive_strategy == 'aggressive':
                bounds = [(1e-6, 100), (0.3, 1.2), (0.0001, 0.0008)]  # 保持较宽范围
            else:
                bounds = [(1e-6, 50), (0.4, 1.0), (0.00015, 0.0007)]  # 默认策略
        else:
            # stage2: 精确优化，使用更严格的参数范围
            if adaptive_strategy == 'conservative':
                bounds = [(1e-6, 10), (0.5, 0.8), (0.0002, 0.0005)]  # 更严格的范围
            elif adaptive_strategy == 'aggressive':
                bounds = [(1e-6, 40), (0.4, 1.0), (0.00018, 0.0006)]  # 相对宽松
            else:
                bounds = [(1e-6, 30), (0.45, 0.9), (0.0002, 0.0006)]  # 默认策略
        
        # 执行优化
        try:
            # 先使用L-BFGS-B方法，通常比Nelder-Mead更快更稳定
            result_lbfgs = minimize(
                self.loss_func, 
                initial_guess, 
                args=(x_data, y_data), 
                method='L-BFGS-B',  # 切换到更适合有界优化的方法
                bounds=bounds
            )
            
            # 再使用Nelder-Mead方法
            result_nelder = minimize(
                self.loss_func, 
                initial_guess, 
                args=(x_data, y_data), 
                method='Nelder-Mead',
                bounds=bounds
            )
            
            # 选择更好的结果
            if result_lbfgs.success and result_nelder.success:
                # 两者都成功，选择损失更小的
                if result_lbfgs.fun < result_nelder.fun:
                    result = result_lbfgs
                else:
                    result = result_nelder
            elif result_lbfgs.success:
                # 只有L-BFGS-B成功
                result = result_lbfgs
            else:
                # 只有Nelder-Mead成功或都失败
                result = result_nelder
            
            a_opt, p_opt, b_opt = result.x
            
            # 确保参数在物理合理范围内
            a_opt = max(1e-6, a_opt)
            p_opt = max(0.4, min(p_opt, 1.2))
            b_opt = max(1e-6, b_opt)
            
            print(f"非线性回归优化完成: a={a_opt:.6f}, p={p_opt:.6f}, b={b_opt:.6f} (策略: {adaptive_strategy}, 误差阈值: {max_error_threshold})")
            return a_opt, p_opt, b_opt
            
        except Exception as e:
            print(f"非线性回归优化失败: {e}")
            # 返回合理的默认值，b基于物理意义设置为0.0004
            return 1.0, 0.8, 0.0004
    
    def predict_K(self, Re, a, p, b):
        """根据非线性回归模型预测传热系数K"""
        try:
            # 使用模型计算Y=1/K
            Y_pred = self.model_func(Re, a, p, b)
            
            # 避免除零错误
            if Y_pred <= 0:
                return 0
            
            # 计算K
            K_pred = 1 / Y_pred
            
            return K_pred
        except Exception as e:
            return 0
    
    def calculate_predicted_K(self, record, a, p, b):
        """
        根据优化的参数预测传热系数K
        """
        try:
            # 从记录中获取雷诺数Re
        if 'reynolds_number' in record:
            Re = record['reynolds_number']
            if Re is not None and Re > 0:
                pass
            else:
                Re = None
        elif 'Re' in record:
            Re = record['Re']
            if Re is not None and Re > 0:
                pass
            else:
                Re = None
            else:
                # 计算Re
                d_i = self.geometry.get('d_i_original', 0.02)
                rho = record.get('density', 1000)
                u = record.get('velocity', 0)
                mu = record.get('dynamic_viscosity', 0.001)
                
                if u <= 0 or mu <= 0:
                    return 0
                
                Re = rho * u * d_i / mu
                
                if Re <= 0:
                    return 0
            
            # 使用模型计算Y=1/K
            Y_pred = self.model_func(Re, a, p, b)
            
            # 避免除零错误
            if Y_pred <= 0:
                return 0
            
            # 计算K
            K_pred = 1 / Y_pred
            
            return K_pred
            
        except Exception as e:
            return 0
    
    def calculate_alpha_i(self, a, p, Re):
        """计算管侧传热系数alpha_i
        alpha_i = 1 / (a * Re^(-p))
        """
        try:
            return 1 / (a * np.power(Re, -p))
        except Exception as e:
            print(f"计算alpha_i失败: {e}")
            return 0
    
    def calculate_fouling_resistance(self, day):
        """根据天数计算壁面热阻R_f
        第0天为0，后续每天按公式 R_f=8e-4*(1−exp(−t/188)) 计算
        返回值单位：m²·K/W
        """
        if day == 0:
            return 0.0
        else:
            return (8e-4 * (1 - np.exp(-day / 188)))
    
    def calculate_alpha_o(self, record):
        """计算壳侧传热系数alpha_o
        从heat_exchanger_monitor_db_test的performance_parameters中读取相同点相同时间戳相同换热器的值
        """
        # 这里简化处理，实际需要从数据库读取
        # 暂时返回一个默认值，后续需要完善
        return record.get('alpha_o', 5000)  # 默认5000 W/(m²·K)