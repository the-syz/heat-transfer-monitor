import pandas as pd
import numpy as np

# 模拟safe_value函数
def safe_value(value):
    """安全地处理pandas/numpy值，转换为Python原生类型或None"""
    if value is None:
        return None
    if pd.isna(value):
        return None
    # 如果是numpy类型，转换为Python原生类型
    if isinstance(value, (np.floating, np.integer)):
        return float(value) if isinstance(value, np.floating) else int(value)
    return value

# 测试alpha_o处理逻辑
def test_alpha_o_processing():
    """测试alpha_o字段的处理逻辑"""
    csv_file = r"e:\BaiduSyncdisk\heat-transfer-monitor\trying-code\calculate-wilosn-reserve\cache\day_1_full_data.csv"
    
    try:
        # 读取CSV文件
        df = pd.read_csv(csv_file)
        
        print(f"文件读取成功，共有 {len(df)} 行数据")
        print(f"alpha_o列的数据类型: {df['alpha_o'].dtype}")
        
        # 模拟导入脚本中的处理逻辑
        print(f"\n测试导入脚本中的alpha_o处理逻辑:")
        
        # 统计结果
        valid_alpha_o = 0
        none_alpha_o = 0
        shellside_h_used = 0
        
        for _, row in df.iterrows():
            # 模拟导入脚本中的处理逻辑
            alpha_o_val = row.get('alpha_o')
            
            print(f"  原始alpha_o_val: {alpha_o_val}, 类型: {type(alpha_o_val)}")
            print(f"  pd.isna(alpha_o_val): {pd.isna(alpha_o_val)}")
            print(f"  alpha_o_val is None: {alpha_o_val is None}")
            
            # 检查是否使用shellside_h
            if pd.isna(alpha_o_val) or alpha_o_val is None:
                alpha_o_val = row.get('shellside_h')
                shellside_h_used += 1
            
            alpha_o_val = safe_value(alpha_o_val)
            
            print(f"  处理后的alpha_o_val: {alpha_o_val}, 类型: {type(alpha_o_val)}")
            
            # 统计结果
            if alpha_o_val is not None:
                valid_alpha_o += 1
            else:
                none_alpha_o += 1
            
            print("  --------------------")
            
            # 只测试前5行
            if _ >= 4:
                break
        
        print(f"\n处理总结:")
        print(f"  总记录数: {len(df)}")
        print(f"  有效alpha_o值: {valid_alpha_o}")
        print(f"  空alpha_o值: {none_alpha_o}")
        print(f"  使用shellside_h的次数: {shellside_h_used}")
        
    except Exception as e:
        print(f"测试时出错: {e}")
        import traceback
        traceback.print_exc()

# 测试特殊情况
def test_special_cases():
    """测试特殊情况"""
    print(f"\n\n测试特殊情况:")
    
    # 测试numpy的NaN值
    np_nan = np.nan
    print(f"numpy的NaN值:")
    print(f"  pd.isna(np_nan): {pd.isna(np_nan)}")
    print(f"  np_nan is None: {np_nan is None}")
    print(f"  safe_value(np_nan): {safe_value(np_nan)}")
    
    # 测试Python的None
    py_none = None
    print(f"\nPython的None:")
    print(f"  pd.isna(py_none): {pd.isna(py_none)}")
    print(f"  py_none is None: {py_none is None}")
    print(f"  safe_value(py_none): {safe_value(py_none)}")
    
    # 测试numpy的float64值
    np_float = np.float64(123.45)
    print(f"\nnumpy的float64值:")
    print(f"  pd.isna(np_float): {pd.isna(np_float)}")
    print(f"  np_float is None: {np_float is None}")
    print(f"  safe_value(np_float): {safe_value(np_float)}")
    print(f"  类型: {type(safe_value(np_float))}")

if __name__ == "__main__":
    test_alpha_o_processing()
    test_special_cases()