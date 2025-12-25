# 数据源配置
DATA_SOURCE_PATHS = {
    'cache': 'e:\\BaiduSyncdisk\\heat-transfer-monitor\\trying-code\\calculate-wilosn-reserve\\cache',
    'data': 'e:\\BaiduSyncdisk\\heat-transfer-monitor\\trying-code\\calculate-wilosn-reserve\\data',
    'result': 'e:\\BaiduSyncdisk\\heat-transfer-monitor\\trying-code\\calculate-wilosn-reserve\\result',
    'result_all_data_in_1': 'e:\\BaiduSyncdisk\\heat-transfer-monitor\\trying-code\\calculate-wilosn-reserve\\result_all_data_in_1'
}

# 数据库配置
DATABASE_CONFIG = {
    'url': 'mysql://root:123456@localhost:3306/heat_exchanger_monitor_db_test',
    'modules': {'models': ['data.test_data.models']}
}

# 基准时间配置
BASE_DATE = '2022-01-01 00:00:00'

# 数据导入配置
IMPORT_CONFIG = {
    'batch_size': 1000,  # 批量导入大小
    'skip_existing': True,  # 是否跳过已存在的数据
    'dry_run': False  # 是否只测试不实际导入数据
}
