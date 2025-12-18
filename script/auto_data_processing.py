#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
数据处理与API调用自动化脚本
功能：
1. 从测试数据库读取数据
2. 定时处理机制（每1分钟模拟1小时）
3. 执行数据计算流程
4. 调用API接口获取参数
5. 保存数据到output文件夹
"""

import os
import time
import json
import requests
import logging
import datetime
from pathlib import Path
from datetime import timedelta

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('auto_data_processing.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class AutoDataProcessor:
    def __init__(self, config_file=None):
        """初始化自动化数据处理器"""
        # 配置文件路径
        self.config_file = config_file or os.path.join(os.path.dirname(__file__), 'config.json')
        self.config = self.load_config()
        
        # API配置
        self.api_url = self.config.get('api_url', 'http://localhost:8000')
        self.api_timeout = self.config.get('api_timeout', 30)
        
        # 数据库配置
        self.db_config = self.config.get('database', {})
        
        # 定时任务配置
        self.interval_minutes = self.config.get('interval_minutes', 1)
        self.start_day = self.config.get('start_day', 1)
        self.start_hour = self.config.get('start_hour', 0)
        self.total_hours = self.config.get('total_hours', 24)
        
        # 输出配置
        self.output_dir = self.config.get('output_dir', os.path.join(os.path.dirname(__file__), '../output'))
        self.output_format = self.config.get('output_format', 'txt')
        
        # 状态跟踪
        self.current_day = self.start_day
        self.current_hour = self.start_hour
        self.processed_hours = 0
        
        # 确保输出目录存在
        self._ensure_output_dir()
        
        logger.info("自动化数据处理器初始化完成")
    
    def load_config(self):
        """加载配置文件"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning(f"配置文件 {self.config_file} 不存在，使用默认配置")
            return self._get_default_config()
        except json.JSONDecodeError as e:
            logger.error(f"配置文件解析错误: {e}")
            raise
    
    def _get_default_config(self):
        """获取默认配置"""
        return {
            'api_url': 'http://localhost:8000',
            'api_timeout': 30,
            'interval_minutes': 1,
            'start_day': 1,
            'start_hour': 0,
            'total_hours': 24,
            'output_dir': os.path.join(os.path.dirname(__file__), '../output'),
            'output_format': 'txt'
        }
    
    def _ensure_output_dir(self):
        """确保输出目录存在"""
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
        logger.info(f"输出目录: {self.output_dir}")
    
    def run_data_processing(self, day, hour):
        """调用API处理指定时间的数据"""
        try:
            url = f"{self.api_url}/process-data/{day}/{hour}"
            response = requests.post(url, timeout=self.api_timeout)
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"数据处理完成 - 第{day}天第{hour}小时: {result['status']}")
                return result['status'] == 'success'
            else:
                logger.warning(f"数据处理API返回错误状态码 {response.status_code} (第{day}天第{hour}小时)")
                try:
                    error_detail = response.json()
                    logger.error(f"API错误详情: {error_detail}")
                except:
                    logger.error(f"API错误内容: {response.text}")
                return False
            
        except requests.RequestException as e:
            logger.error(f"调用数据处理API失败 (第{day}天第{hour}小时): {e}")
            return False
        except Exception as e:
            logger.error(f"数据处理过程中发生错误 (第{day}天第{hour}小时): {e}")
            return False
    
    def get_api_data(self, endpoint, params=None):
        """调用API获取数据"""
        try:
            url = f"{self.api_url}/{endpoint}"
            response = requests.get(url, params=params, timeout=self.api_timeout)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"调用API失败 ({endpoint}): {e}")
            return None
        except Exception as e:
            logger.error(f"获取API数据时发生错误 ({endpoint}): {e}")
            return None
    
    def save_data_to_file(self, data, day, hour):
        """保存数据到文件"""
        try:
            # 生成文件名
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"data_hour_{day}_{hour}_{timestamp}.{self.output_format}"
            filepath = os.path.join(self.output_dir, filename)
            
            # 格式化数据
            if self.output_format.lower() == 'json':
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
            else:  # txt格式
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(f"=== 第{day}天第{hour}小时数据 ({timestamp}) ===\n\n")
                    
                    # 写入状态信息
                    if data.get('status'):
                        f.write(f"状态: {data['status']}\n")
                        f.write(f"数据数量: {data.get('count', 0)}\n\n")
                    
                    # 写入具体数据
                    for i, item in enumerate(data.get('data', []), 1):
                        f.write(f"--- 数据项 {i} ---")
                        for key, value in item.items():
                            f.write(f"{key}: {value}\n")
                        f.write("\n")
            
            logger.info(f"数据已保存到文件: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"保存数据到文件失败: {e}")
            return None
    
    def process_single_hour(self):
        """处理单个小时的数据"""
        logger.info(f"开始处理第{self.current_day}天第{self.current_hour}小时的数据")
        
        # 1. 调用API处理数据
        if not self.run_data_processing(self.current_day, self.current_hour):
            logger.error(f"第{self.current_day}天第{self.current_hour}小时的数据处理失败")
            return False
        
        # 等待API处理完成
        time.sleep(2)
        
        # 2. 获取运行参数数据
        logger.info("获取运行参数数据")
        operation_params = self.get_api_data('operation-parameters', {
            'day': self.current_day,
            'hour': self.current_hour
        })
        
        # 3. 获取物理参数数据
        logger.info("获取物理参数数据")
        physical_params = self.get_api_data('physical-parameters', {
            'day': self.current_day,
            'hour': self.current_hour
        })
        
        # 4. 获取性能参数数据
        logger.info("获取性能参数数据")
        performance_params = self.get_api_data('performance', {
            'day': self.current_day,
            'hour': self.current_hour
        })
        
        # 5. 获取K管理数据
        logger.info("获取K管理数据")
        k_management = self.get_api_data('k-management', {
            'day': self.current_day,
            'hour': self.current_hour
        })
        
        # 6. 保存所有数据到文件
        all_data = {
            'day': self.current_day,
            'hour': self.current_hour,
            'operation_parameters': operation_params,
            'physical_parameters': physical_params,
            'performance_parameters': performance_params,
            'k_management': k_management
        }
        
        self.save_data_to_file(all_data, self.current_day, self.current_hour)
        
        logger.info(f"第{self.current_day}天第{self.current_hour}小时的数据处理完成")
        return True
    
    def _update_time(self):
        """更新当前时间（模拟增加1小时）"""
        self.current_hour += 1
        self.processed_hours += 1
        
        # 处理小时进位
        if self.current_hour >= 24:
            self.current_hour = 0
            self.current_day += 1
    
    def run(self):
        """启动自动化数据处理流程"""
        logger.info("开始自动化数据处理流程")
        logger.info(f"处理间隔: {self.interval_minutes} 分钟/小时")
        logger.info(f"总处理小时数: {self.total_hours}")
        
        try:
            while self.processed_hours < self.total_hours:
                # 处理当前小时
                success = self.process_single_hour()
                
                if not success:
                    logger.warning(f"第{self.current_day}天第{self.current_hour}小时处理失败，将在下次尝试")
                    time.sleep(60 * self.interval_minutes)
                    continue
                
                # 更新到下一小时
                self._update_time()
                
                # 检查是否需要继续
                if self.processed_hours >= self.total_hours:
                    break
                
                # 等待下一个处理周期
                logger.info(f"等待 {self.interval_minutes} 分钟进行下一次处理...")
                time.sleep(60 * self.interval_minutes)
                
        except KeyboardInterrupt:
            logger.info("自动化数据处理流程被用户中断")
        except Exception as e:
            logger.error(f"自动化数据处理流程发生错误: {e}", exc_info=True)
        finally:
            logger.info("自动化数据处理流程结束")
            logger.info(f"总共处理了 {self.processed_hours} 个小时的数据")


def main():
    """主函数"""
    try:
        # 创建自动化数据处理器实例
        processor = AutoDataProcessor()
        
        # 启动处理流程
        processor.run()
        
    except Exception as e:
        logger.error(f"程序运行失败: {e}", exc_info=True)
        exit(1)


if __name__ == "__main__":
    main()