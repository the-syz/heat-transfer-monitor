import sys
import os
import json

# 添加backend目录到Python路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

from db.db_connection import DatabaseConnection

# 读取配置文件
config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend', 'config', 'config.json'))

# 创建数据库连接对象
db_conn = DatabaseConnection(config_path)

# 连接到生产数据库
if db_conn.connect_prod_db():
    try:
        # 查询k_management表中K_predicted字段的统计信息
        print('k_management表中K_predicted字段的统计信息:')
        query = "SELECT COUNT(*) as total, SUM(CASE WHEN K_predicted IS NOT NULL THEN 1 ELSE 0 END) as positive_k_predicted FROM k_management"
        if db_conn.execute_query(db_conn.prod_cursor, query):
            result = db_conn.prod_cursor.fetchone()
            print(f'总记录数: {result["total"]}')
            print(f'K_predicted不为空的记录数: {result["positive_k_predicted"]}')

        # 查询k_management表中K_predicted字段的前5条有值的记录
        print('\nk_management表中K_predicted字段的前5条有值的记录:')
        query = "SELECT heat_exchanger_id, timestamp, K_predicted, K_actual FROM k_management WHERE K_predicted IS NOT NULL LIMIT 5"
        if db_conn.execute_query(db_conn.prod_cursor, query):
            results = db_conn.prod_cursor.fetchall()
            for row in results:
                print(f'换热器ID: {row["heat_exchanger_id"]}, 时间戳: {row["timestamp"]}, K_predicted: {row["K_predicted"]}, K_actual: {row["K_actual"]}')

    except Exception as e:
        print(f"查询过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # 断开数据库连接
        db_conn.disconnect_prod_db()
else:
    print("连接数据库失败")