from tortoise import Tortoise, run_async
from models import HeatExchanger

async def init_test_db():
    # 数据库连接配置 - 使用test数据库
    await Tortoise.init(
        db_url='mysql://heatexMCP:123123@localhost:3306/heat_exchanger_monitor_db_test',
        modules={'models': ['models']}
    )
    
    # 创建表结构
    await Tortoise.generate_schemas()
    
    # 检查换热器表是否已有数据
    existing_he = await HeatExchanger.first()
    if not existing_he:
        # 填充换热器表数据
        await HeatExchanger.create(
            id=1,
            type="管壳式换热器",
            tube_side_fluid="水",
            shell_side_fluid="轻柴油",
            tube_section_count=30,
            shell_section_count=19,
            d_i_original=0.02,
            d_o=0.025,
            lambda_t=45.0
        )
        print("换热器表数据已填充")
    else:
        print("换热器表已有数据，跳过填充")
    
    print("Test数据库初始化完成！")
    
    # 关闭连接
    await Tortoise.close_connections()

if __name__ == "__main__":
    run_async(init_test_db())
