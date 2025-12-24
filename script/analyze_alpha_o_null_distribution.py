import sys
import os

# 添加backend目录到Python路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

# 连接数据库
try:
    from db.db_connection import DatabaseConnection
    
    # 创建数据库连接对象
    config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend', 'config', 'config.json'))
    db_conn = DatabaseConnection(config_path)
    
    # 连接到测试数据库
    if db_conn.connect_test_db():
        try:
            print("=== alpha_o字段空值分布分析 ===")
            
            # 1. 按日期统计alpha_o字段的空值分布
            print("\n1. 按日期统计alpha_o字段的空值分布:")
            query = """SELECT DATE(timestamp) AS date, 
                        COUNT(*) AS total, 
                        COUNT(alpha_o) AS non_null_alpha_o, 
                        (COUNT(*) - COUNT(alpha_o)) AS null_alpha_o 
                    FROM performance_parameters 
                    GROUP BY DATE(timestamp) 
                    ORDER BY date"""
            
            if db_conn.execute_query(db_conn.test_cursor, query):
                results = db_conn.fetch_all(db_conn.test_cursor)
                print(f"日期\t\t总记录数\t非空记录数\t空记录数\t非空比例")
                print("-" * 80)
                for row in results:
                    date = row['date']
                    total = row['total']
                    non_null = row['non_null_alpha_o']
                    null_count = row['null_alpha_o']
                    non_null_ratio = non_null/total*100 if total > 0 else 0
                    print(f"{date}\t{total}\t\t{non_null}\t\t{null_count}\t\t{non_null_ratio:.2f}%")
            
            # 2. 查看最近30天的记录情况
            print("\n2. 查看最近30天的记录情况:")
            query = """SELECT DATE(timestamp) AS date, 
                        COUNT(*) AS total, 
                        COUNT(alpha_o) AS non_null_alpha_o, 
                        (COUNT(*) - COUNT(alpha_o)) AS null_alpha_o 
                    FROM performance_parameters 
                    GROUP BY DATE(timestamp) 
                    ORDER BY date DESC 
                    LIMIT 30"""
            
            if db_conn.execute_query(db_conn.test_cursor, query):
                results = db_conn.fetch_all(db_conn.test_cursor)
                print(f"日期\t\t总记录数\t非空记录数\t空记录数\t非空比例")
                print("-" * 80)
                for row in results:
                    date = row['date']
                    total = row['total']
                    non_null = row['non_null_alpha_o']
                    null_count = row['null_alpha_o']
                    non_null_ratio = non_null/total*100 if total > 0 else 0
                    print(f"{date}\t{total}\t\t{non_null}\t\t{null_count}\t\t{non_null_ratio:.2f}%")
                    
            # 3. 查看最早30天的记录情况
            print("\n3. 查看最早30天的记录情况:")
            query = """SELECT DATE(timestamp) AS date, 
                        COUNT(*) AS total, 
                        COUNT(alpha_o) AS non_null_alpha_o, 
                        (COUNT(*) - COUNT(alpha_o)) AS null_alpha_o 
                    FROM performance_parameters 
                    GROUP BY DATE(timestamp) 
                    ORDER BY date ASC 
                    LIMIT 30"""
            
            if db_conn.execute_query(db_conn.test_cursor, query):
                results = db_conn.fetch_all(db_conn.test_cursor)
                print(f"日期\t\t总记录数\t非空记录数\t空记录数\t非空比例")
                print("-" * 80)
                for row in results:
                    date = row['date']
                    total = row['total']
                    non_null = row['non_null_alpha_o']
                    null_count = row['null_alpha_o']
                    non_null_ratio = non_null/total*100 if total > 0 else 0
                    print(f"{date}\t{total}\t\t{non_null}\t\t{null_count}\t\t{non_null_ratio:.2f}%")
                    
            # 4. 查看特定日期的具体数据
            print("\n4. 查看最近一天记录的alpha_o字段详情:")
            query = """SELECT id, timestamp, points, alpha_o, K 
                        FROM performance_parameters 
                        ORDER BY timestamp DESC 
                        LIMIT 50"""
            
            if db_conn.execute_query(db_conn.test_cursor, query):
                results = db_conn.fetch_all(db_conn.test_cursor)
                print(f"ID\t\tTimestamp\t\t\tPoints\tAlpha_o\tK")
                print("-" * 80)
                for row in results[:10]:  # 只显示前10条
                    print(f"{row['id']}\t{row['timestamp']}\t{row['points']}\t{row['alpha_o']}\t{row['K']}")
                print(f"... 共 {len(results)} 条记录")
                        
        finally:
            # 断开数据库连接
            db_conn.disconnect_test_db()
    else:
        print("连接数据库失败")
        
except Exception as e:
    print(f"发生错误: {e}")
    import traceback
    traceback.print_exc()