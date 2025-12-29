import sys
import os
import json

# 将backend目录添加到Python路径
sys.path.insert(0, os.path.abspath('e:\\BaiduSyncdisk\\heat-transfer-monitor\\backend'))

from db.db_connection import DatabaseConnection

def check_k_management_full():
    try:
        # 读取配置文件
        config_file = 'e:\\BaiduSyncdisk\\heat-transfer-monitor\\config.json'
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # 创建数据库连接对象
        db_conn = DatabaseConnection(config)
        
        # 连接生产数据库
        if not db_conn.connect_prod_db():
            print("无法连接到生产数据库")
            return
        
        print("成功连接到生产数据库")
        
        # 执行SHOW CREATE TABLE查询
        query = 'SHOW CREATE TABLE k_management'
        if db_conn.execute_query(db_conn.prod_cursor, query):
            result = db_conn.fetch_one(db_conn.prod_cursor)
            if result:
                print("\nk_management表的完整创建语句:")
                print(result['Create Table'])
        
        # 执行SELECT查询查看表结构
        query = 'DESCRIBE k_management'
        if db_conn.execute_query(db_conn.prod_cursor, query):
            result = db_conn.fetch_all(db_conn.prod_cursor)
            print("\nk_management表的字段结构:")
            for row in result:
                print(row)
        
        # 执行SHOW INDEX查询查看索引结构
        query = 'SHOW INDEX FROM k_management'
        if db_conn.execute_query(db_conn.prod_cursor, query):
            result = db_conn.fetch_all(db_conn.prod_cursor)
            print("\nk_management表的索引结构:")
            for row in result:
                print(row)
        
        # 关闭数据库连接
        db_conn.disconnect_prod_db()
        print("\n数据库连接已关闭")
        
    except Exception as e:
        print(f"检查k_management表时发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_k_management_full()