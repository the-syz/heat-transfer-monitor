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
        print("分析performance_parameters表中alpha_o字段为空值的记录分布：\n")
        
        # 1. 按换热器ID分组，统计每个换热器的空值记录数量
        print("1. 按换热器ID分组的空值记录数量：")
        query1 = "SELECT heat_exchanger_id, COUNT(*) as null_count FROM performance_parameters WHERE alpha_o IS NULL GROUP BY heat_exchanger_id ORDER BY null_count DESC"
        if db_conn.execute_query(db_conn.test_cursor, query1):
            result1 = db_conn.fetch_all(db_conn.test_cursor)
            for row in result1:
                print(f"  换热器ID {row['heat_exchanger_id']}: {row['null_count']} 条空值记录")
        
        # 2. 按时间范围分组，统计每个月的空值记录数量
        print("\n2. 按时间范围（月份）分组的空值记录数量：")
        query2 = "SELECT DATE_FORMAT(timestamp, '%Y-%m') as month, COUNT(*) as null_count FROM performance_parameters WHERE alpha_o IS NULL GROUP BY month ORDER BY month"
        if db_conn.execute_query(db_conn.test_cursor, query2):
            result2 = db_conn.fetch_all(db_conn.test_cursor)
            for row in result2:
                print(f"  {row['month']}: {row['null_count']} 条空值记录")
        
        # 3. 统计非空记录的数量，计算空值比例
        print("\n3. 空值比例统计：")
        query3 = "SELECT COUNT(*) as total_count FROM performance_parameters"
        if db_conn.execute_query(db_conn.test_cursor, query3):
            total_count = db_conn.fetch_one(db_conn.test_cursor)['total_count']
            
            query4 = "SELECT COUNT(*) as null_count FROM performance_parameters WHERE alpha_o IS NULL"
            if db_conn.execute_query(db_conn.test_cursor, query4):
                null_count = db_conn.fetch_one(db_conn.test_cursor)['null_count']
                non_null_count = total_count - null_count
                null_ratio = (null_count / total_count) * 100 if total_count > 0 else 0
                
                print(f"  总记录数: {total_count}")
                print(f"  空值记录数: {null_count}")
                print(f"  非空记录数: {non_null_count}")
                print(f"  空值比例: {null_ratio:.2f}%")
    finally:
        # 断开数据库连接
        db_conn.disconnect_test_db()
else:
    print("连接数据库失败")
