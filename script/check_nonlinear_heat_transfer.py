import pandas as pd
import os
import glob

# 检查nonlinear_regression下的heat_transfer.csv文件结构
def check_nonlinear_heat_transfer():
    """检查nonlinear_regression下的heat_transfer.csv文件结构"""
    # 获取所有nonlinear_regression目录下的heat_transfer.csv文件
    base_dir = r"e:\BaiduSyncdisk\heat-transfer-monitor\trying-code\calculate-wilosn-reserve\result"
    file_pattern = os.path.join(base_dir, "nonlinear_regression", "points_T*", "heat_transfer_coefficients", "*.csv")
    
    print(f"正在查找文件: {file_pattern}")
    
    files = glob.glob(file_pattern)
    print(f"找到 {len(files)} 个文件")
    
    if not files:
        print("未找到任何文件")
        return
    
    # 检查第一个文件的结构
    first_file = files[0]
    print(f"\n检查第一个文件: {first_file}")
    
    try:
        df = pd.read_csv(first_file)
        
        print(f"\n文件读取成功，形状: {df.shape}")
        print(f"\n列名列表:")
        for i, col in enumerate(df.columns):
            print(f"  [{i+1}] {repr(col)}")  # 使用repr显示列名的原始表示
        
        # 检查alpha_o列
        print(f"\nalpha_o列信息:")
        if 'alpha_o' in df.columns:
            alpha_o_col = df['alpha_o']
            print(f"  alpha_o列的数据类型: {alpha_o_col.dtype}")
            print(f"  alpha_o列的非空值数量: {alpha_o_col.count()}")
            print(f"  alpha_o列的空值数量: {alpha_o_col.isna().sum()}")
            print(f"  alpha_o列的前5个值:")
            print(alpha_o_col.head())
        else:
            print(f"  未找到alpha_o列")
            
        # 检查K_actual列
        print(f"\nK_actual列信息:")
        if 'K_actual' in df.columns:
            k_actual_col = df['K_actual']
            print(f"  K_actual列的数据类型: {k_actual_col.dtype}")
            print(f"  K_actual列的非空值数量: {k_actual_col.count()}")
            print(f"  K_actual列的空值数量: {k_actual_col.isna().sum()}")
            print(f"  K_actual列的前5个值:")
            print(k_actual_col.head())
        else:
            print(f"  未找到K_actual列")
            
    except Exception as e:
        print(f"\n读取文件时出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_nonlinear_heat_transfer()