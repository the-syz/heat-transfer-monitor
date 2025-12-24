import asyncio

from data.test_data.models import PerformanceParameter
from script.data_import.utils import init_db

async def main():
    # 初始化数据库连接
    await init_db()
    
    print("开始检查PerformanceParameter表中alpha_o字段的空值情况...")
    
    # 统计总记录数
    total_records = await PerformanceParameter.all().count()
    print(f"总记录数: {total_records}")
    
    # 统计alpha_o为空的记录数
    null_alpha_o_count = await PerformanceParameter.filter(alpha_o__isnull=True).count()
    print(f"alpha_o为空的记录数: {null_alpha_o_count}")
    
    # 计算空值率
    null_rate = (null_alpha_o_count / total_records) * 100 if total_records > 0 else 0
    print(f"alpha_o空值率: {null_rate:.2f}%")
    
    # 检查alpha_i的空值情况
    null_alpha_i_count = await PerformanceParameter.filter(alpha_i__isnull=True).count()
    print(f"\nalpha_i为空的记录数: {null_alpha_i_count}")
    print(f"alpha_i空值率: {(null_alpha_i_count / total_records) * 100:.2f}%")
    
    # 打印一些示例记录
    print("\n部分alpha_o非空的记录:")
    non_null_records = await PerformanceParameter.filter(alpha_o__isnull=False).order_by('timestamp').limit(10)
    for record in non_null_records[:5]:
        print(f"  时间: {record.timestamp}, alpha_o: {record.alpha_o}, alpha_i: {record.alpha_i}, K: {record.K}")
    
    print("\n部分alpha_o为空的记录:")
    null_records = await PerformanceParameter.filter(alpha_o__isnull=True).order_by('timestamp').limit(10)
    for record in null_records[:5]:
        print(f"  时间: {record.timestamp}, alpha_o: {record.alpha_o}, alpha_i: {record.alpha_i}, K: {record.K}")
    
    # 分析结果
    print("\n分析结果:")
    if null_rate < 50:
        print("✅ alpha_o空值率已经显著降低，修复基本成功！")
    else:
        print("❌ alpha_o空值率仍然较高，可能需要进一步检查数据来源。")

if __name__ == "__main__":
    asyncio.run(main())
