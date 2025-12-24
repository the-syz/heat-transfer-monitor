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
        # 查询performance_parameters表的结构
        query = "DESCRIBE performance_parameters"
        if db_conn.execute_query(db_conn.test_cursor, query):
            print("performance_parameters表的结构：")
            structure = db_conn.fetch_all(db_conn.test_cursor)
            for field in structure:
                print(f"字段名: {field['Field']}, 类型: {field['Type']}, 是否为空: {field['Null']}, 键: {field['Key']}, 默认值: {field['Default']}, 额外信息: {field['Extra']}")
        else:
            print("查询表结构失败")
    finally:
        # 断开数据库连接
        db_conn.disconnect_test_db()
else:
    print("连接数据库失败")
