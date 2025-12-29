import sys
import os

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
        # 查询k_management表的结构
        print("k_management表的结构:")
        query = "DESCRIBE k_management"
        if db_conn.execute_query(db_conn.prod_cursor, query):
            results = db_conn.prod_cursor.fetchall()
            for row in results:
                print(f"字段名: {row['Field']}, 类型: {row['Type']}, 是否允许空: {row['Null']}, 主键: {row['Key']}")

        # 查询k_management表的主键定义
        print("\nk_management表的主键定义:")
        query = "SHOW INDEX FROM k_management WHERE Key_name = 'PRIMARY'"
        if db_conn.execute_query(db_conn.prod_cursor, query):
            results = db_conn.prod_cursor.fetchall()
            for row in results:
                print(f"字段名: {row['Column_name']}, 排序: {row['Seq_in_index']}")

    except Exception as e:
        print(f"查询过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # 断开数据库连接
        db_conn.disconnect_prod_db()
else:
    print("连接数据库失败")
