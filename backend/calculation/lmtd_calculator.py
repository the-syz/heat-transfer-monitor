import numpy as np

class LMTDCalculator:
    def __init__(self):
        pass
    
    def calculate_lmtd(self, T_h_in, T_h_out, T_c_in, T_c_out, flow_type='counterflow'):
        """计算对数平均温差
        
        参数:
            T_h_in: 热流体入口温度 (°C)
            T_h_out: 热流体出口温度 (°C)
            T_c_in: 冷流体入口温度 (°C)
            T_c_out: 冷流体出口温度 (°C)
            flow_type: 流动类型，'counterflow'（逆流）或'parallel'（并流）
        
        返回:
            LMTD值
        """
        try:
            # 添加None值检查
            if T_h_in is None or T_h_out is None or T_c_in is None or T_c_out is None:
                return 0
                
            if flow_type == 'parallel':
                # 并流情况
                delta_T1 = T_h_in - T_c_in
                delta_T2 = T_h_out - T_c_out
            else:
                # 逆流情况
                delta_T1 = T_h_in - T_c_out
                delta_T2 = T_h_out - T_c_in
            
            # 计算LMTD
            if delta_T1 == delta_T2:
                return delta_T1
            elif delta_T1 <= 0 or delta_T2 <= 0:
                return 0
            else:
                return (delta_T1 - delta_T2) / np.log(delta_T1 / delta_T2)
        except Exception as e:
            print(f"计算LMTD失败: {e}")
            return 0
    
    def calculate_k_lmtd(self, Q, A, lmtd):
        """使用LMTD方法计算总传热系数K_lmtd
        
        参数:
            Q: 传热量 (W)
            A: 换热面积 (m²)
            lmtd: 对数平均温差 (°C)
        
        返回:
            K_lmtd值 (W/(m²·K))
        """
        try:
            # 添加None值检查
            if Q is None or A is None or lmtd is None:
                return 0
                
            if A <= 0 or lmtd <= 0:
                return 0
            return Q / (A * lmtd)
        except Exception as e:
            print(f"计算K_lmtd失败: {e}")
            return 0
    
    def calculate_heat_transfer_rate(self, flow_rate, specific_heat, delta_T):
        """计算传热量
        
        参数:
            flow_rate: 流体流量 (kg/s)
            specific_heat: 流体比热容 (J/(kg·K))
            delta_T: 流体温度变化 (°C)
        
        返回:
            传热量 (W)
        """
        try:
            # 添加None值检查
            if flow_rate is None or specific_heat is None or delta_T is None:
                return 0
                
            return flow_rate * specific_heat * delta_T
        except Exception as e:
            print(f"计算传热量失败: {e}")
            return 0
    
    def calculate_k_lmtd_from_data(self, data, heat_exchanger_area=1.0):
        """从数据中计算K_lmtd
        
        参数:
            data: 包含温度、流量等参数的数据
            heat_exchanger_area: 换热面积 (m²)
        
        返回:
            K_lmtd值 (W/(m²·K))
        """
        # 这里简化处理，假设数据中包含计算所需的所有参数
        # 实际应用中需要根据具体数据结构进行调整
        try:
            # 假设数据中包含冷热流体的温度和流量
            T_h_in = data.get('T_h_in', 0)
            T_h_out = data.get('T_h_out', 0)
            T_c_in = data.get('T_c_in', 0)
            T_c_out = data.get('T_c_out', 0)
            flow_rate = data.get('flow_rate', 0)
            specific_heat = data.get('specific_heat', 4186)  # 默认水的比热容
            
            # 计算LMTD
            lmtd = self.calculate_lmtd(T_h_in, T_h_out, T_c_in, T_c_out)
            
            # 计算传热量
            delta_T = abs(T_h_in - T_h_out)
            Q = self.calculate_heat_transfer_rate(flow_rate, specific_heat, delta_T)
            
            # 计算K_lmtd
            K_lmtd = self.calculate_k_lmtd(Q, heat_exchanger_area, lmtd)
            
            return K_lmtd
        except Exception as e:
            print(f"从数据计算K_lmtd失败: {e}")
            return 0