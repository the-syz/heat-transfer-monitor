import mysql.connector

# 连接到数据库
try:
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='123456',
        database='heat_exchanger_monitor_db'
    )
    
    cursor = conn.cursor()
    
    # 查询model_parameters表结构
    print('model_parameters表结构:')
    cursor.execute('DESCRIBE model_parameters')
    for row in cursor:
        print(row)
    
    # 查询k_management表结构
    print('\nk_management表结构:')
    cursor.execute('DESCRIBE k_management')
    for row in cursor:
        print(row)
    
    # 查询performance_parameters表结构
    print('\nperformance_parameters表结构:')
    cursor.execute('DESCRIBE performance_parameters')
    for row in cursor:
        print(row)
    
    conn.close()
    print('\n查询完成')
    
except Exception as e:
    print(f'查询错误: {e}')