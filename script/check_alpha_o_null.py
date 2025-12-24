import sys
import os

# 添加backend目录到Python路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

from db.db_connection import DatabaseConnection

# 创建数据库连接对象
config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend', 'config', 'config.json'))
db_conn = DatabaseConnection(config_path)

# 连接到测试数据库
if db_conn.connect_test_db():
    try:
        # 执行查询，检查performance_parameters表的alpha_o字段是否有空值
        query = "SELECT COUNT(*) as null_count FROM performance_parameters WHERE alpha_o IS NULL"
        if db_conn.execute_query(db_conn.test_cursor, query):
            result = db_conn.fetch_one(db_conn.test_cursor)
            null_count = result['null_count']
            
            if null_count > 0:
                print(f"发现 {null_count} 条记录的 alpha_o 字段为空值")
                
                # 查看前10条空值记录的详细信息
                print("\n前10条空值记录的详细信息：")
                query_details = "SELECT id, heat_exchanger_id, timestamp, alpha_o FROM performance_parameters WHERE alpha_o IS NULL LIMIT 10"
                if db_conn.execute_query(db_conn.test_cursor, query_details):
                    details = db_conn.fetch_all(db_conn.test_cursor)
                    for record in details:
                        print(f"ID: {record['id']}, 换热器ID: {record['heat_exchanger_id']}, 时间戳: {record['timestamp']}, alpha_o: {record['alpha_o']}")
            else:
                print("performance_parameters表的alpha_o字段中没有空值")
        else:
            print("执行查询失败")
    finally:
        # 断开数据库连接
        db_conn.disconnect_test_db()
else:
    print("连接数据库失败")
