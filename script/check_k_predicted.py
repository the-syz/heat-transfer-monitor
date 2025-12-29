import sys
import os

# 添加backend目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

from db.db_connection import DatabaseConnection
import json

try:
    # 读取配置文件
    config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend', 'config', 'config.json'))
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    # 创建数据库连接对象
    db_conn = DatabaseConnection(config)
    
    # 连接生产数据库
    db_conn.connect_prod_db()
    
    print("成功连接到生产数据库")
    
    # 查询k_management表中K_predicted字段的统计信息
    db_conn.execute_query(db_conn.prod_cursor, "SELECT COUNT(*) as total_records, SUM(CASE WHEN K_predicted IS NOT NULL THEN 1 ELSE 0 END) as non_null_records FROM k_management")
    result = db_conn.fetch_one(db_conn.prod_cursor)
    
    print(f"总记录数: {result['total_records']}")
    print(f"K_predicted不为空的记录数: {result['non_null_records']}")
    
    # 查询前5条K_predicted有值的记录
    print("\n前5条K_predicted有值的记录:")
    db_conn.execute_query(db_conn.prod_cursor, "SELECT heat_exchanger_id, timestamp, points, side, K_predicted FROM k_management WHERE K_predicted IS NOT NULL LIMIT 5")
    results = db_conn.fetch_all(db_conn.prod_cursor)
    
    for record in results:
        print(record)
    
    # 关闭数据库连接
    db_conn.disconnect_prod_db()
    
    print("\n数据库连接已关闭")
    
except Exception as e:
    print(f"发生错误: {str(e)}")
    import traceback
    traceback.print_exc()