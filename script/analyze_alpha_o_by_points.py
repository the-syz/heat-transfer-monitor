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
            print("=== alpha_o字段与points值关系分析 ===")
            
            # 1. 按points值统计alpha_o字段的空值分布
            print("\n1. 按points值统计alpha_o字段的空值分布:")
            query = """SELECT points, 
                        COUNT(*) AS total, 
                        COUNT(alpha_o) AS non_null_alpha_o, 
                        (COUNT(*) - COUNT(alpha_o)) AS null_alpha_o 
                    FROM performance_parameters 
                    GROUP BY points 
                    ORDER BY points"""
            
            if db_conn.execute_query(db_conn.test_cursor, query):
                results = db_conn.fetch_all(db_conn.test_cursor)
                print(f"Points\t总记录数\t非空记录数\t空记录数\t非空比例")
                print("-" * 80)
                for row in results:
                    points = row['points']
                    total = row['total']
                    non_null = row['non_null_alpha_o']
                    null_count = row['null_alpha_o']
                    non_null_ratio = non_null/total*100 if total > 0 else 0
                    print(f"{points}\t{total}\t\t{non_null}\t\t{null_count}\t\t{non_null_ratio:.2f}%")
            
            # 2. 查看特定points值的记录情况
            print("\n2. 查看不同points值的记录示例:")
            
            # 查看有alpha_o值的points示例
            query = """SELECT id, timestamp, points, alpha_o, K 
                        FROM performance_parameters 
                        WHERE alpha_o IS NOT NULL 
                        LIMIT 5"""
            
            if db_conn.execute_query(db_conn.test_cursor, query):
                results = db_conn.fetch_all(db_conn.test_cursor)
                print("\n有alpha_o值的记录示例:")
                print(f"ID\t\tTimestamp\t\t\tPoints\tAlpha_o\tK")
                for row in results:
                    print(f"{row['id']}\t{row['timestamp']}\t{row['points']}\t{row['alpha_o']}\t{row['K']}")
                    
            # 查看无alpha_o值的points示例
            query = """SELECT id, timestamp, points, alpha_o, K 
                        FROM performance_parameters 
                        WHERE alpha_o IS NULL 
                        LIMIT 5"""
            
            if db_conn.execute_query(db_conn.test_cursor, query):
                results = db_conn.fetch_all(db_conn.test_cursor)
                print("\n无alpha_o值的记录示例:")
                print(f"ID\t\tTimestamp\t\t\tPoints\tAlpha_o\tK")
                for row in results:
                    print(f"{row['id']}\t{row['timestamp']}\t{row['points']}\t{row['alpha_o']}\t{row['K']}")
            
            # 3. 检查最近一天数据的points分布
            print("\n3. 检查最近一天数据的points分布:")
            query = """SELECT DISTINCT points 
                        FROM performance_parameters 
                        WHERE timestamp >= DATE_SUB(NOW(), INTERVAL 1 DAY) 
                        ORDER BY points"""
            
            if db_conn.execute_query(db_conn.test_cursor, query):
                results = db_conn.fetch_all(db_conn.test_cursor)
                points_list = [row['points'] for row in results]
                print(f"最近一天数据包含的points值: {points_list}")
                print(f"共 {len(points_list)} 个不同的points值")
                
                # 检查有alpha_o值的points
                query = """SELECT DISTINCT points 
                            FROM performance_parameters 
                            WHERE timestamp >= DATE_SUB(NOW(), INTERVAL 1 DAY) 
                            AND alpha_o IS NOT NULL 
                            ORDER BY points"""
                
                if db_conn.execute_query(db_conn.test_cursor, query):
                    results = db_conn.fetch_all(db_conn.test_cursor)
                    non_null_points = [row['points'] for row in results]
                    print(f"有alpha_o值的points: {non_null_points}")
                    print(f"共 {len(non_null_points)} 个points有alpha_o值")
                    
                    # 检查无alpha_o值的points
                    query = """SELECT DISTINCT points 
                                FROM performance_parameters 
                                WHERE timestamp >= DATE_SUB(NOW(), INTERVAL 1 DAY) 
                                AND alpha_o IS NULL 
                                ORDER BY points"""
                    
                    if db_conn.execute_query(db_conn.test_cursor, query):
                        results = db_conn.fetch_all(db_conn.test_cursor)
                        null_points = [row['points'] for row in results]
                        print(f"无alpha_o值的points: {null_points}")
                        print(f"共 {len(null_points)} 个points无alpha_o值")
            
        finally:
            # 断开数据库连接
            db_conn.disconnect_test_db()
    else:
        print("连接数据库失败")
        
except Exception as e:
    print(f"发生错误: {e}")
    import traceback
    traceback.print_exc()