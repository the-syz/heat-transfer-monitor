import pandas as pd
import os

# 检查heat_transfer.csv文件中的alpha_o字段
def check_heat_transfer_csv():
    """检查heat_transfer.csv文件中的alpha_o字段"""
    heat_transfer_file = r"e:\BaiduSyncdisk\heat-transfer-monitor\trying-code\calculate-wilosn-reserve\result_all_data_in_1\two_stage_linear\heat_transfer_coefficients\day_1_heat_transfer.csv"
    
    print(f"检查文件: {heat_transfer_file}")
    print(f"文件是否存在: {os.path.exists(heat_transfer_file)}")
    
    try:
        # 读取CSV文件
        df = pd.read_csv(heat_transfer_file)
        
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
            print(f"  alpha_o列的最后5个值:")
            print(alpha_o_col.tail())
        else:
            print(f"  未找到alpha_o列")
            
        # 检查K_actual和alpha_i列
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
            
        print(f"\nalpha_i列信息:")
        if 'alpha_i' in df.columns:
            alpha_i_col = df['alpha_i']
            print(f"  alpha_i列的数据类型: {alpha_i_col.dtype}")
            print(f"  alpha_i列的非空值数量: {alpha_i_col.count()}")
            print(f"  alpha_i列的空值数量: {alpha_i_col.isna().sum()}")
            print(f"  alpha_i列的前5个值:")
            print(alpha_i_col.head())
        else:
            print(f"  未找到alpha_i列")
            
    except Exception as e:
        print(f"\n读取文件时出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_heat_transfer_csv()