import os
import sys
from datetime import datetime
import asyncio
from tortoise import Tortoise

# 添加项目根目录到Python路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 从data.test_data.models导入PerformanceParameter模型
from data.test_data.models import PerformanceParameter

async def verify_alpha_o():
    try:
        # 初始化数据库连接
        await Tortoise.init(
            db_url='mysql://heatexMCP:123123@localhost:3306/heat_exchanger_monitor_db_test',
            modules={'models': ['data.test_data.models']}
        )
        
        # 查询总记录数
        total_count = await PerformanceParameter.all().count()
        print(f"总记录数: {total_count}")
        
        # 查询alpha_o字段不为空的记录数
        non_empty_count = await PerformanceParameter.filter(alpha_o__isnull=False).count()
        print(f"alpha_o字段不为空的记录数: {non_empty_count}")
        
        # 计算非空比例
        if total_count > 0:
            non_empty_ratio = (non_empty_count / total_count) * 100
            print(f"alpha_o字段非空比例: {non_empty_ratio:.2f}%")
        
        # 查询alpha_o字段为空的记录数（应该为0）
        empty_count = await PerformanceParameter.filter(alpha_o__isnull=True).count()
        print(f"alpha_o字段为空的记录数: {empty_count}")
        
        # 查询alpha_o字段值为5000的记录数（默认值）
        default_value_count = await PerformanceParameter.filter(alpha_o=5000).count()
        print(f"alpha_o字段值为默认值5000的记录数: {default_value_count}")
        
        # 查询alpha_o字段值不为5000的记录数（实际从CSV文件导入的值）
        actual_value_count = await PerformanceParameter.filter(alpha_o__not=5000).count()
        print(f"alpha_o字段值为实际导入值的记录数: {actual_value_count}")
        
        # 验证数据完整性
        if non_empty_count == total_count and empty_count == 0:
            print("\n✅ 验证成功: 所有PerformanceParameter记录的alpha_o字段都有值！")
        else:
            print("\n❌ 验证失败: 仍有alpha_o字段为空的记录！")
            
    except Exception as e:
        print(f"\n❌ 验证过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # 关闭数据库连接
        await Tortoise.close_connections()

# 运行验证函数
if __name__ == "__main__":
    print("=== alpha_o字段完整性验证 ===")
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    asyncio.run(verify_alpha_o())
    print(f"结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=== 验证完成 ===")
