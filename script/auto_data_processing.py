import json
import os
import sys
import time
import logging
import requests
import datetime

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.db.db_connection import DatabaseConnection
from backend.calculation.main_calculator import MainCalculator

# 配置日志记录
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('auto_data_processing.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class Config:
    """配置类，管理脚本的各种配置参数"""
    def __init__(self):
        self.config_file = os.path.join(os.path.dirname(__file__), '..', 'backend', 'config', 'config.json')
        self.load_config()
        
        # API配置
        self.api_base_url = "http://localhost:8000"
        self.api_timeout = 30
        
        # 定时处理配置
        self.time_interval = 60  # 秒，每1分钟处理一次
        self.start_day = 1
        self.start_hour = 0
        
        # 输出配置
        self.output_folder = "output"
        os.makedirs(self.output_folder, exist_ok=True)
        
        # 管段参数配置
        self.target_section_id = 1  # 目标管段ID
        
    def load_config(self):
        """从文件加载配置"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
            logger.info(f"成功加载配置文件: {self.config_file}")
        except Exception as e:
            logger.error(f"加载配置文件失败: {e}")
            self.config = {}

class DatabaseHandler:
    """数据库处理类，负责与数据库交互"""
    def __init__(self, config):
        self.config = config
        self.db_conn = DatabaseConnection(self.config.config_file)
        self.connect_databases()
    
    def connect_databases(self):
        """连接数据库"""
        try:
            self.db_conn.connect_test_db()
            self.db_conn.connect_prod_db()
            logger.info("成功连接到数据库")
        except Exception as e:
            logger.error(f"连接数据库失败: {e}")
    
    def disconnect_databases(self):
        """断开数据库连接"""
        try:
            self.db_conn.disconnect_test_db()
            self.db_conn.disconnect_prod_db()
            logger.info("成功断开数据库连接")
        except Exception as e:
            logger.error(f"断开数据库连接失败: {e}")
    
    def get_data_by_hour(self, day, hour):
        """获取指定天数和小时的数据"""
        try:
            # 从测试数据库读取运行参数
            operation_data = self.db_conn.data_loader.get_operation_parameters_by_hour(day, hour)
            
            # 从测试数据库读取物理参数
            physical_data = self.db_conn.data_loader.get_physical_parameters_by_hour(day, hour)
            
            # 从测试数据库读取性能参数
            performance_data = self.db_conn.data_loader.get_performance_parameters_by_hour(day, hour)
            
            logger.info(f"成功获取第{day}天第{hour}小时的数据")
            return operation_data, physical_data, performance_data
        except Exception as e:
            logger.error(f"获取数据失败: {e}")
            return [], [], []

class APIClient:
    """API客户端类，负责与API交互"""
    def __init__(self, config):
        self.config = config
        self.base_url = self.config.api_base_url
        self.timeout = self.config.api_timeout
    
    def process_data(self, day, hour):
        """调用API处理数据"""
        try:
            url = f"{self.base_url}/process-data/{day}/{hour}"
            response = requests.post(url, timeout=self.timeout)
            response.raise_for_status()
            result = response.json()
            logger.info(f"成功调用API处理第{day}天第{hour}小时的数据")
            return result
        except Exception as e:
            logger.error(f"调用API处理数据失败: {e}")
            return None
    
    def get_section_parameters(self, heat_exchanger_id, day, hour):
        """获取特定管段的参数"""
        try:
            url = f"{self.base_url}/operation-parameters"
            params = {
                "heat_exchanger_id": heat_exchanger_id,
                "day": day,
                "hour": hour
            }
            response = requests.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            result = response.json()
            logger.info(f"成功获取管段参数: heat_exchanger_id={heat_exchanger_id}, day={day}, hour={hour}")
            return result
        except Exception as e:
            logger.error(f"获取管段参数失败: {e}")
            return None

class DataProcessor:
    """数据处理类，负责执行计算流程"""
    def __init__(self, config, db_handler):
        self.config = config
        self.db_handler = db_handler
        self.calculator = MainCalculator(self.config.config_file)
    
    def process_hourly_data(self, day, hour):
        """处理每小时数据"""
        try:
            logger.info(f"开始处理第{day}天第{hour}小时的数据")
            
            # 执行计算流程
            success = self.calculator.process_data_by_hour(day, hour)
            
            if success:
                logger.info(f"第{day}天第{hour}小时的数据处理成功")
                return True
            else:
                logger.error(f"第{day}天第{hour}小时的数据处理失败")
                return False
        except Exception as e:
            logger.error(f"处理数据时发生错误: {e}")
            return False

class OutputManager:
    """输出管理类，负责保存结果文件"""
    def __init__(self, config):
        self.config = config
    
    def save_section_parameters(self, data, day, hour):
        """保存管段参数到TXT文件"""
        try:
            # 生成时间戳
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # 生成文件名
            filename = f"section_params_day{day}_hour{hour}_{timestamp}.txt"
            filepath = os.path.join(self.config.output_folder, filename)
            
            # 保存数据
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"管段参数数据 - 第{day}天第{hour}小时\n")
                f.write(f"生成时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("=" * 50 + "\n")
                
                if 'data' in data and data['data']:
                    for item in data['data']:
                        f.write("\n管段数据:\n")
                        for key, value in item.items():
                            f.write(f"{key}: {value}\n")
                        f.write("-" * 30 + "\n")
                else:
                    f.write("没有找到管段数据\n")
            
            logger.info(f"成功保存管段参数到文件: {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"保存管段参数失败: {e}")
            return None

class AutoProcessor:
    """自动处理器类，协调各个组件完成自动化任务"""
    def __init__(self):
        self.config = Config()
        self.db_handler = DatabaseHandler(self.config)
        self.api_client = APIClient(self.config)
        self.data_processor = DataProcessor(self.config, self.db_handler)
        self.output_manager = OutputManager(self.config)
        
        # 初始化当前时间
        self.current_day = self.config.start_day
        self.current_hour = self.config.start_hour
    
    def process_cycle(self):
        """执行一个处理周期"""
        try:
            logger.info(f"\n=== 开始处理周期: 第{self.current_day}天第{self.current_hour}小时 ===")
            
            # 1. 从数据库读取数据
            operation_data, physical_data, performance_data = self.db_handler.get_data_by_hour(self.current_day, self.current_hour)
            
            if not operation_data and not physical_data and not performance_data:
                logger.warning(f"第{self.current_day}天第{self.current_hour}小时没有数据，跳过处理")
            else:
                # 2. 执行计算流程
                processing_success = self.data_processor.process_hourly_data(self.current_day, self.current_hour)
                
                if processing_success:
                    # 3. 调用API获取特定管段参数
                    section_params = self.api_client.get_section_parameters(
                        self.config.target_section_id, 
                        self.current_day, 
                        self.current_hour
                    )
                    
                    if section_params:
                        # 4. 保存结果到文件
                        self.output_manager.save_section_parameters(
                            section_params, 
                            self.current_day, 
                            self.current_hour
                        )
            
            # 更新当前时间
            self.update_current_time()
            
            logger.info(f"=== 处理周期完成: 第{self.current_day-1}天第{self.current_hour-1 if self.current_hour > 0 else 23}小时 ===")
            return True
            
        except Exception as e:
            logger.error(f"处理周期失败: {e}")
            return False
    
    def update_current_time(self):
        """更新当前时间（增加1小时）"""
        self.current_hour += 1
        if self.current_hour >= 24:
            self.current_hour = 0
            self.current_day += 1
    
    def run(self):
        """启动自动处理流程"""
        logger.info("启动自动数据处理与API调用脚本")
        logger.info(f"时间间隔: {self.config.time_interval}秒")
        logger.info(f"输出文件夹: {self.config.output_folder}")
        
        try:
            while True:
                self.process_cycle()
                logger.info(f"等待{self.config.time_interval}秒后开始下一个处理周期...")
                time.sleep(self.config.time_interval)
        except KeyboardInterrupt:
            logger.info("收到停止信号，正在退出...")
        except Exception as e:
            logger.error(f"自动处理流程发生错误: {e}")
        finally:
            self.db_handler.disconnect_databases()
            logger.info("自动处理流程已停止")

if __name__ == "__main__":
    auto_processor = AutoProcessor()
    auto_processor.run()