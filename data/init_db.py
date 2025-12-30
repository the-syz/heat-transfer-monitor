from tortoise import Tortoise, run_async
from models import HeatExchanger
import aiomysql

async def init_db():
    # 数据库连接配置
    await Tortoise.init(
        db_url='mysql://heatexMCP:123123@localhost:3306/heat_exchanger_monitor_db',
        modules={'models': ['models']}
    )
    
    # 创建表结构
    await Tortoise.generate_schemas()
    
    # 手动添加新字段（如果不存在）
    try:
        conn = Tortoise.get_connection("default")
        async with conn._pool.acquire() as connection:
            async with connection.cursor() as cursor:
                # 先查询现有字段
                await cursor.execute("DESCRIBE heat_exchanger")
                existing_columns = {row[0] for row in await cursor.fetchall()}
                
                # 定义需要添加的字段
                new_fields = [
                    ("heat_exchange_area", "FLOAT NULL COMMENT '换热面积 (m²)'"),
                    ("tube_passes", "INT NULL COMMENT '管程数'"),
                    ("shell_passes", "INT NULL COMMENT '壳程数'"),
                    ("tube_wall_thickness", "FLOAT NULL COMMENT '换热管壁厚 (m)'"),
                    ("tube_length", "FLOAT NULL COMMENT '换热管长度 (m)'"),
                    ("tube_count", "INT NULL COMMENT '换热管数'"),
                    ("tube_arrangement", "VARCHAR(50) NULL COMMENT '换热管布置形式'"),
                    ("tube_pitch", "FLOAT NULL COMMENT '换热管间距 (m)'"),
                    ("shell_inner_diameter", "FLOAT NULL COMMENT '壳体内径 (m)'"),
                    ("baffle_type", "VARCHAR(50) NULL COMMENT '折流板类型'"),
                    ("baffle_cut_ratio", "FLOAT NULL COMMENT '折流板切口率'"),
                    ("baffle_spacing", "FLOAT NULL COMMENT '折流板间距 (m)'")
                ]
                
                # 只添加不存在的字段
                for field_name, field_def in new_fields:
                    if field_name not in existing_columns:
                        try:
                            stmt = f"ALTER TABLE heat_exchanger ADD COLUMN {field_name} {field_def}"
                            await cursor.execute(stmt)
                            print(f"已添加字段: {field_name}")
                        except Exception as e:
                            print(f"添加字段 {field_name} 时出错: {e}")
                    else:
                        print(f"字段 {field_name} 已存在，跳过")
    except Exception as e:
        print(f"添加新字段时出错: {e}")
        # 如果出错，继续执行，让Tortoise处理
        pass
    
    # 检查换热器表是否已有数据
    existing_he = await HeatExchanger.first()
    if not existing_he:
        # 填充换热器表数据（根据表2.4的结构尺寸）
        await HeatExchanger.create(
            id=1,
            type="管壳式换热器",
            tube_side_fluid="Water",
            shell_side_fluid="Light Diesel Oil",
            tube_section_count=30,
            shell_section_count=19,
            d_i_original=0.02,  # 管内径 = 外径 - 2*壁厚 = 0.025 - 2*0.0025 = 0.02
            d_o=0.025,  # 管外径 25mm = 0.025m
            lambda_t=45.0,
            # 新增字段
            heat_exchange_area=188.0,  # 换热面积 188 m²
            tube_passes=2,  # 管程数 2
            shell_passes=1,  # 壳程数 1
            tube_wall_thickness=0.0025,  # 壁厚 2.5mm = 0.0025m
            tube_length=9.0,  # 换热管长度 9 m
            tube_count=268,  # 换热管数 268
            tube_arrangement="转角正方形",  # 换热管布置形式
            tube_pitch=0.032,  # 换热管间距 32mm = 0.032m
            shell_inner_diameter=0.7,  # 壳体内径 700mm = 0.7m
            baffle_type="单弓形",  # 折流板类型
            baffle_cut_ratio=0.25,  # 折流板切口率 25% = 0.25
            baffle_spacing=0.2  # 折流板间距 200mm = 0.2m
        )
        print("换热器表数据已填充")
    else:
        # 如果已有数据，更新新增的字段
        await HeatExchanger.filter(id=1).update(
            heat_exchange_area=188.0,
            tube_passes=2,
            shell_passes=1,
            tube_wall_thickness=0.0025,
            tube_length=9.0,
            tube_count=268,
            tube_arrangement="转角正方形",
            tube_pitch=0.032,
            shell_inner_diameter=0.7,
            baffle_type="单弓形",
            baffle_cut_ratio=0.25,
            baffle_spacing=0.2
        )
        print("换热器表数据已更新")
    
    print("数据库初始化完成！")
    
    # 关闭连接
    await Tortoise.close_connections()

if __name__ == "__main__":
    run_async(init_db())
