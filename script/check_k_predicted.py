import sys
import os
sys.path.insert(0, os.path.abspath('.'))
from backend.db.data_loader import DataLoader

# 初始化数据库连接
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '123456',
    'database': 'heat_transfer_monitor'
}
data_loader = DataLoader(db_config)

# 连接数据库
data_loader.connect()

# 查询k_management表中K_predicted字段的统计信息
query = "SELECT COUNT(*) as total, SUM(CASE WHEN K_predicted IS NOT NULL THEN 1 ELSE 0 END) as positive_k_predicted FROM k_management"
result = data_loader.execute_query(query)
print('k_management表中K_predicted字段的统计信息:')
if result:
    print(f'总记录数: {result[0][0]}')
    print(f'K_predicted不为空的记录数: {result[0][1]}')

# 查询k_management表中K_predicted字段的前5条有值的记录
query = "SELECT heat_exchanger_id, timestamp, K_predicted, K_actual FROM k_management WHERE K_predicted IS NOT NULL LIMIT 5"
result = data_loader.execute_query(query)
print('\nk_management表中K_predicted字段的前5条有值的记录:')
for row in result:
    print(f'换热器ID: {row[0]}, 时间戳: {row[1]}, K_predicted: {row[2]}, K_actual: {row[3]}')

# 断开数据库连接
data_loader.disconnect()
