import os
import sys
import asyncio

# 设置工作目录到项目根目录
base_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(base_dir)

# 导入所需模块
from script.data_import.import_data import import_cache_full_data, import_heat_transfer_data
from data.test_data.models import PerformanceParameter
from script.data_import.utils import init_db

async def main():
    print("开始测试alpha_o字段修复...")
    
    # 1. 初始化数据库连接
    await init_db()
    
    # 2. 先清空现有数据
    print("2. 清空现有PerformanceParameter数据...")
    await PerformanceParameter.all().delete()
    
    # 3. 导入一个full_data文件
    full_data_file = r'trying-code\calculate-wilosn-reserve\cache\day_1_full_data.csv'
    print(f"3. 导入full_data文件: {os.path.basename(full_data_file)}")
    await import_cache_full_data(full_data_file)
    
    # 4. 检查导入后的alpha_o值
    print("\n4. 检查导入后的alpha_o值:")
    records = await PerformanceParameter.all().order_by('timestamp').limit(10)
    non_null_alpha_o = sum(1 for r in records if r.alpha_o is not None)
    for record in records[:5]:
        print(f"   ID: {record.id}, alpha_o: {record.alpha_o}")
    print(f"   统计: 前10条记录中alpha_o非空数量: {non_null_alpha_o}")
    
    # 5. 导入一个heat_transfer文件
    heat_transfer_file = r'trying-code\calculate-wilosn-reserve\result_all_data_in_1\two_stage_linear\heat_transfer_coefficients\day_1_heat_transfer.csv'
    print(f"\n5. 导入heat_transfer文件: {os.path.basename(heat_transfer_file)}")
    await import_heat_transfer_data(heat_transfer_file)
    
    # 6. 再次检查alpha_o值
    print("\n6. 再次检查alpha_o值 (确保没有被覆盖为空):")
    records = await PerformanceParameter.all().order_by('timestamp').limit(10)
    non_null_alpha_o_after = sum(1 for r in records if r.alpha_o is not None)
    for record in records[:5]:
        print(f"   ID: {record.id}, alpha_o: {record.alpha_o}")
    print(f"   统计: 前10条记录中alpha_o非空数量: {non_null_alpha_o_after}")
    
    # 7. 检查结果
    if non_null_alpha_o_after == non_null_alpha_o and non_null_alpha_o > 0:
        print("\n✅ 测试通过! alpha_o值没有被heat_transfer文件覆盖为空。")
    else:
        print("\n❌ 测试失败! alpha_o值被覆盖为空。")

if __name__ == "__main__":
    asyncio.run(main())
