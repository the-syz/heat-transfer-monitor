import sys
import os
from datetime import datetime
import asyncio
import pandas as pd

# 添加项目根目录到Python路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from data.test_data.models import (
    OperationParameter
)
from utils import (
    init_db,
    close_db,
    process_points,
    convert_to_timestamp,
    read_csv_file,
    batch_insert,
    get_all_csv_files
)
from config import DATA_SOURCE_PATHS, IMPORT_CONFIG

# 从指定路径读取壳侧操作参数数据
async def import_shell_operation_data(file_path):
    """导入壳侧操作参数数据
    
    Args:
        file_path (str): 文件路径
        
    Returns:
        dict: 导入结果统计
    """
    print(f"处理文件: {os.path.basename(file_path)}")
    
    # 读取CSV文件
    df = read_csv_file(file_path)
    if df is None:
        return {"file": file_path, "success": False, "message": "读取文件失败"}
    
    # 初始化数据列表
    operation_data = []
    
    # 处理每行数据
    for _, row in df.iterrows():
        # 处理points和side
        points_str = row.get('points', '')
        points, side = process_points(str(points_str))
        
        # 只处理壳侧数据
        if points is None or side != 'shell':
            continue
        
        # 获取day和hour
        day = row.get('day', 0)
        hour = row.get('hour', 0)
        
        if isinstance(day, str):
            try:
                day = int(float(day))
            except ValueError:
                day = 0
        
        if isinstance(hour, str):
            try:
                hour = int(float(hour))
            except ValueError:
                hour = 0
        
        # 转换为时间戳
        timestamp = convert_to_timestamp(day, hour)
        
        # 换热器编号，默认为1
        heat_exchanger_id = 1
        
        # 运行参数数据
        operation_param = OperationParameter(
            heat_exchanger_id=heat_exchanger_id,
            timestamp=timestamp,
            points=points,
            side=side,
            temperature=row.get('temperature'),
            pressure=row.get('pressure'),
            flow_rate=row.get('flow_rate'),
            velocity=row.get('velocity')
        )
        operation_data.append(operation_param)
    
    # 批量插入数据
    inserted_counts = {}
    
    if operation_data:
        inserted_counts['operation_parameters'] = await batch_insert(OperationParameter, operation_data, IMPORT_CONFIG['batch_size'])
    
    return {
        "file": file_path,
        "success": True,
        "inserted_counts": inserted_counts
    }



# 验证壳侧数据完整性
async def verify_shell_data_integrity():
    """验证壳侧数据的完整性"""
    print("\n=== 数据完整性验证 ===")
    
    # 导入必要的模型
    from data.test_data.models import HeatExchanger
    
    # 获取换热器列表
    heat_exchangers = await HeatExchanger.all()
    
    for hx in heat_exchangers:
        print(f"\n换热器 {hx.id} 数据统计:")
        
        # 运行参数统计
        op_count = await OperationParameter.filter(heat_exchanger=hx, side='shell').count()
        print(f"  运行参数: {op_count} 条")

# 主导入函数
async def main():
    """壳侧数据导入主函数"""
    print("=== 壳侧数据导入工具 ===")
    print(f"开始时间: {datetime.now().strftime('%H:%M:%S')}")
    
    # 数据源路径
    data_path = 'e:\\BaiduSyncdisk\\heat-transfer-monitor\\trying-code\\calculate-wilosn-reserve\\data'
    print(f"数据源: {data_path}")
    
    # 初始化数据库连接
    await init_db()
    
    try:
        # 结果统计
        total_results = []
        
        # 获取所有操作参数文件
        all_files = get_all_csv_files(data_path)
        operation_files = [f for f in all_files if 'operation_parameters.csv' in f]
        print(f"\n找到 {len(operation_files)} 个操作参数文件")
        
        for file_path in operation_files:
            result = await import_shell_operation_data(file_path)
            total_results.append(result)
        
        # 打印导入结果汇总
        print("\n=== 导入结果汇总 ===")
        success_count = 0
        total_inserted = {
            'operation_parameters': 0
        }
        
        for result in total_results:
            if result['success']:
                success_count += 1
                # 累加插入数量
                for key, value in result['inserted_counts'].items():
                    total_inserted[key] += value
            else:
                print(f"✗ {os.path.basename(result['file'])}: {result.get('message', '失败')}")
        
        print(f"\n处理文件数: {len(total_results)}")
        print(f"成功: {success_count}")
        print(f"失败: {len(total_results) - success_count}")
        
        print("\n插入数据统计:")
        for key, value in total_inserted.items():
            print(f"  {key.replace('_', ' ').title()}: {value} 条")
        
        # 验证数据完整性
        await verify_shell_data_integrity()
        
        print(f"\n=== 导入完成 ===")
        print(f"结束时间: {datetime.now().strftime('%H:%M:%S')}")
        
    except Exception as e:
        print(f"\n导入过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # 关闭数据库连接
        await close_db()

# 运行主函数
if __name__ == "__main__":
    asyncio.run(main())