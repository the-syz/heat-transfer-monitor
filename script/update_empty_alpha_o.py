#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
更新数据库中所有alpha_o字段为空的记录
"""

import asyncio
from tortoise import Tortoise
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 从data.models导入PerformanceParameter
from data.models import PerformanceParameter

async def update_empty_alpha_o():
    """更新所有alpha_o字段为空的记录"""
    try:
        # 初始化数据库连接
        await Tortoise.init(
            db_url='mysql://root:admin@localhost:3306/heat_transfer_monitor',
            modules={'models': ['backend.models']}
        )
        await Tortoise.generate_schemas()
        
        print("正在更新alpha_o字段为空的记录...")
        
        # 更新所有alpha_o字段为空的记录
        updated_count = await PerformanceParameter.filter(alpha_o__isnull=True).update(alpha_o=5000)
        
        print(f"成功更新了 {updated_count} 条alpha_o字段为空的记录")
        
        # 验证更新结果
        total_empty = await PerformanceParameter.filter(alpha_o__isnull=True).count()
        print(f"更新后，alpha_o字段为空的记录数: {total_empty}")
        
    except Exception as e:
        print(f"更新过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # 关闭数据库连接
        await Tortoise.close_connections()

if __name__ == "__main__":
    asyncio.run(update_empty_alpha_o())