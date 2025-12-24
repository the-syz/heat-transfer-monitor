import pymysql
import pymysql.cursors
from urllib.parse import urlparse
from script.data_import.config import DATABASE_CONFIG

def parse_db_url(db_url):
    """
    解析数据库URL为连接参数
    """
    parsed = urlparse(db_url)
    return {
        'host': parsed.hostname,
        'port': parsed.port,
        'user': parsed.username,
        'password': parsed.password,
        'database': parsed.path.strip('/')
    }

def check_k_null_values():
    """
    检查数据库中K值的空值情况
    """
    try:
        # 解析数据库连接URL
        db_params = parse_db_url(DATABASE_CONFIG['url'])
        
        # 连接数据库
        connection = pymysql.connect(
            host=db_params['host'],
            port=db_params['port'],
            user=db_params['user'],
            password=db_params['password'],
            database=db_params['database'],
            cursorclass=pymysql.cursors.DictCursor
        )
        
        with connection.cursor() as cursor:
            # 1. 检查k_predictions表的结构
            print("=== 检查k_predictions表结构 ===")
            cursor.execute("DESCRIBE k_predictions")
            k_predictions_structure = cursor.fetchall()
            for field in k_predictions_structure:
                print(f"字段名: {field['Field']}, 类型: {field['Type']}, 是否允许空: {field['Null']}")
            
            # PerformanceParameter表不存在，跳过检查
            
            # 2. 统计k_predictions表中K值的空值情况
            print("\n=== k_predictions表K值空值统计 ===")
            # 检查K_predicted字段
            cursor.execute("SELECT COUNT(*) AS total FROM k_predictions")
            total_k = cursor.fetchone()['total']
            
            cursor.execute("SELECT COUNT(*) AS null_count FROM k_predictions WHERE K_predicted IS NULL")
            null_k = cursor.fetchone()['null_count']
            
            null_rate_k = (null_k / total_k) * 100 if total_k > 0 else 0
            print(f"总记录数: {total_k}")
            print(f"K_predicted空值数量: {null_k}")
            print(f"K_predicted空值率: {null_rate_k:.2f}%")
            
            # 3. 检查数据库中所有表名
            print("\n=== 数据库中所有表名 ===")
            cursor.execute("SHOW TABLES")
            all_tables = cursor.fetchall()
            for table in all_tables:
                print(f"  - {list(table.values())[0]}")
            
            # 4. 查看部分k_predictions记录
            print("\n=== k_predictions表前10条记录示例 ===")
            cursor.execute("SELECT * FROM k_predictions LIMIT 10")
            sample_records = cursor.fetchall()
            for i, record in enumerate(sample_records):
                print(f"记录 {i+1}:")
                print(f"  时间戳: {record.get('timestamp')}")
                print(f"  K值: {record.get('K_predicted')}")
                print(f"  其他参数: heat_exchanger_id={record.get('heat_exchanger_id')}, side={record.get('side')}")
                print()
            
            # 5. 检查performance_parameters表中是否有K相关字段
            print("\n=== 检查performance_parameters表结构 ===")
            cursor.execute("DESCRIBE performance_parameters")
            performance_structure = cursor.fetchall()
            k_fields_in_performance = []
            for field in performance_structure:
                print(f"字段名: {field['Field']}, 类型: {field['Type']}, 是否允许空: {field['Null']}")
                if 'k_' in field['Field'].lower() or 'kvalue' in field['Field'].lower() or 'k' == field['Field'].lower():
                    k_fields_in_performance.append(field['Field'])
            
            if k_fields_in_performance:
                print("\n=== performance_parameters表K值空值统计 ===")
                for k_field in k_fields_in_performance:
                    cursor.execute(f"SELECT COUNT(*) AS total FROM performance_parameters")
                    total = cursor.fetchone()['total']
                    
                    cursor.execute(f"SELECT COUNT(*) AS null_count FROM performance_parameters WHERE {k_field} IS NULL")
                    null_count = cursor.fetchone()['null_count']
                    
                    null_rate = (null_count / total) * 100 if total > 0 else 0
                    print(f"字段 {k_field}:")
                    print(f"  总记录数: {total}")
                    print(f"  空值数量: {null_count}")
                    print(f"  空值率: {null_rate:.2f}%")
            else:
                print("\n=== performance_parameters表中未找到K相关字段 ===")
            
    except Exception as e:
        print(f"检查过程中出现错误: {str(e)}")
    finally:
        if 'connection' in locals():
            connection.close()

if __name__ == "__main__":
    print("开始检查数据库中K值的空值情况...")
    check_k_null_values()
    print("检查完成！")