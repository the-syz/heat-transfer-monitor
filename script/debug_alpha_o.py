import pandas as pd
import os

# 测试读取CSV文件
def test_read_csv():
    """测试CSV文件读取，检查alpha_o字段"""
    csv_file = r"e:\BaiduSyncdisk\heat-transfer-monitor\trying-code\calculate-wilosn-reserve\cache\day_1_full_data.csv"
    
    print(f"读取文件: {csv_file}")
    print(f"文件是否存在: {os.path.exists(csv_file)}")
    
    try:
        # 读取CSV文件
        df = pd.read_csv(csv_file)
        
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
            
        # 检查是否有类似alpha_o的列
        print(f"\n检查类似alpha_o的列:")
        for col in df.columns:
            if 'alpha' in col.lower():
                print(f"  找到列: {repr(col)}")
        
        # 检查shellside_h列
        print(f"\n检查shellside_h列:")
        if 'shellside_h' in df.columns:
            shellside_h_col = df['shellside_h']
            print(f"  shellside_h列的数据类型: {shellside_h_col.dtype}")
            print(f"  shellside_h列的非空值数量: {shellside_h_col.count()}")
            print(f"  shellside_h列的空值数量: {shellside_h_col.isna().sum()}")
            print(f"  shellside_h列的前5个值:")
            print(shellside_h_col.head())
        else:
            print(f"  未找到shellside_h列")
            
    except Exception as e:
        print(f"\n读取文件时出错: {e}")
        import traceback
        traceback.print_exc()

# 检查行数据处理
def test_row_processing():
    """测试行数据处理"""
    csv_file = r"e:\BaiduSyncdisk\heat-transfer-monitor\trying-code\calculate-wilosn-reserve\cache\day_1_full_data.csv"
    
    try:
        df = pd.read_csv(csv_file)
        
        print(f"\n测试行数据处理:")
        # 取第一行数据进行测试
        first_row = df.iloc[0]
        print(f"\n第一行数据:")
        
        # 测试row.get('alpha_o')和直接访问
        print(f"  使用row.get('alpha_o'): {first_row.get('alpha_o')}")
        print(f"  直接访问row['alpha_o']: {first_row['alpha_o']}")
        print(f"  使用pd.isna(): {pd.isna(first_row['alpha_o'])}")
        print(f"  使用is None: {first_row['alpha_o'] is None}")
        
        # 检查数据类型
        print(f"  alpha_o数据类型: {type(first_row['alpha_o'])}")
        
    except Exception as e:
        print(f"\n处理行数据时出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_read_csv()
    test_row_processing()