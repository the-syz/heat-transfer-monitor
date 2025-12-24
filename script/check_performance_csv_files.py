import sys
import os
import pandas as pd

# 添加script/data_import目录到Python路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'script', 'data_import')))

from config import DATA_SOURCE_PATHS

# 检查performance_parameters.csv文件的内容
def check_performance_csv_files():
    """检查performance_parameters.csv文件的内容"""
    print("=== 检查performance_parameters.csv文件内容 ===")
    
    # 获取data目录
    data_dir = DATA_SOURCE_PATHS['data']
    if not os.path.exists(data_dir):
        print(f"数据目录不存在: {data_dir}")
        return
    
    # 获取所有CSV文件
    csv_files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]
    performance_files = [f for f in csv_files if 'performance_parameters' in f]
    
    print(f"找到 {len(performance_files)} 个performance_parameters文件")
    
    for file_name in performance_files:
        file_path = os.path.join(data_dir, file_name)
        print(f"\n检查文件: {file_path}")
        
        try:
            # 读取CSV文件
            df = pd.read_csv(file_path)
            print(f"文件包含 {len(df)} 行数据，{len(df.columns)} 列")
            
            # 检查列名
            print(f"列名: {list(df.columns)}")
            
            # 检查alpha_o和shellside_h字段
            has_alpha_o = 'alpha_o' in df.columns
            has_shellside_h = 'shellside_h' in df.columns
            
            print(f"包含alpha_o字段: {has_alpha_o}")
            print(f"包含shellside_h字段: {has_shellside_h}")
            
            # 检查alpha_o字段的数据
            if has_alpha_o:
                non_null_alpha_o = df['alpha_o'].count()
                null_alpha_o = len(df) - non_null_alpha_o
                print(f"alpha_o字段非空值数: {non_null_alpha_o}, 空值数: {null_alpha_o}")
                
                # 显示前5行数据
                print("\nalpha_o字段前5行数据:")
                print(df[['alpha_o']].head())
            
            # 检查shellside_h字段的数据
            if has_shellside_h:
                non_null_shellside_h = df['shellside_h'].count()
                null_shellside_h = len(df) - non_null_shellside_h
                print(f"shellside_h字段非空值数: {non_null_shellside_h}, 空值数: {null_shellside_h}")
                
                # 显示前5行数据
                print("\nshellside_h字段前5行数据:")
                print(df[['shellside_h']].head())
            
            # 检查K字段的数据
            if 'K' in df.columns:
                non_null_K = df['K'].count()
                null_K = len(df) - non_null_K
                print(f"K字段非空值数: {non_null_K}, 空值数: {null_K}")
                
        except Exception as e:
            print(f"读取文件失败: {e}")
    
    # 检查cache full_data文件的内容
    print("\n=== 检查cache full_data文件内容 ===")
    cache_files = get_all_csv_files(DATA_SOURCE_PATHS['cache'])
    cache_full_data_files = [f for f in cache_files if 'full_data' in f]
    
    print(f"找到 {len(cache_full_data_files)} 个cache full_data文件")
    
    # 只检查第一个full_data文件
    if cache_full_data_files:
        file_path = cache_full_data_files[0]
        print(f"\n检查文件: {file_path}")
        
        try:
            # 读取CSV文件
            df = pd.read_csv(file_path)
            print(f"文件包含 {len(df)} 行数据，{len(df.columns)} 列")
            
            # 检查alpha_o字段
            has_alpha_o = 'alpha_o' in df.columns
            print(f"包含alpha_o字段: {has_alpha_o}")
            
            if has_alpha_o:
                non_null_alpha_o = df['alpha_o'].count()
                null_alpha_o = len(df) - non_null_alpha_o
                print(f"alpha_o字段非空值数: {non_null_alpha_o}, 空值数: {null_alpha_o}")
                
                # 显示前5行数据
                print("\nalpha_o字段前5行数据:")
                print(df[['alpha_o']].head())
                
        except Exception as e:
            print(f"读取文件失败: {e}")

# 获取所有CSV文件
def get_all_csv_files(directory):
    """获取目录下所有CSV文件"""
    csv_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.csv'):
                csv_files.append(os.path.join(root, file))
    return csv_files

if __name__ == "__main__":
    check_performance_csv_files()