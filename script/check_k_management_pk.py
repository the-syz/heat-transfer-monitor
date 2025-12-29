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
    
    # 查询k_management表的主键和索引信息
    print("\n表结构:")
    db_conn.execute_query(db_conn.prod_cursor, "DESCRIBE k_management")
    results = db_conn.fetch_all(db_conn.prod_cursor)
    for row in results:
        print(row)
    
    print("\n索引信息:")
    db_conn.execute_query(db_conn.prod_cursor, "SHOW INDEX FROM k_management")
    results = db_conn.fetch_all(db_conn.prod_cursor)
    for row in results:
        print(row)
    
    print("\n表创建语句:")
    db_conn.execute_query(db_conn.prod_cursor, "SHOW CREATE TABLE k_management")
    result = db_conn.fetch_one(db_conn.prod_cursor)
    print(result['Create Table'])
    
    # 查询前5条记录，看看实际数据结构
    print("\n前5条记录:")
    db_conn.execute_query(db_conn.prod_cursor, "SELECT * FROM k_management LIMIT 5")
    results = db_conn.fetch_all(db_conn.prod_cursor)
    for row in results:
        print(row)
    
    # 关闭数据库连接
    db_conn.disconnect_prod_db()
    
    print("\n数据库连接已关闭")
    
except Exception as e:
    print(f"发生错误: {str(e)}")
    import traceback
    traceback.print_exc()