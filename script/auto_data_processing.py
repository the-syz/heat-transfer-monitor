#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
自动化数据处理脚本

功能：
1. 从测试数据库读取数据
2. 每间隔1分钟，模拟增加1小时的时间来读取该小时段内的全部数据
3. 对每个小时段的完整数据执行预设的计算流程
4. 调用指定API接口获取特定管段的指定参数
5. 将API获取的数据以TXT格式保存至output文件夹

脚本包含错误处理机制、日志记录功能以及配置模块
"""

import os
import sys
import json
import time
import logging
import requests
import schedule
import datetime
from pathlib import Path
from typing import Dict, List, Any

# 添加backend目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))

# 导入backend模块
try:
    from db.db_connection import DatabaseConnection
    from calculation.main_calculator import MainCalculator
except ImportError as e:
    logging.error(f"导入backend模块失败: {e}")
    sys.exit(1)

# 配置日志
def setup_logging():
    """设置日志配置"""
    logger = logging.getLogger('auto_data_processing')
    logger.setLevel(logging.INFO)
    
    # 创建文件处理器
    log_file = os.path.join(os.path.dirname(__file__), 'auto_data_processing.log')
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    
    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # 设置日志格式
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # 添加处理器
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

# 加载配置
def load_config():
    """加载配置文件"""
    config_path = os.path.join(os.path.dirname(__file__), 'config.json')
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        return config
    except FileNotFoundError:
        logger.error(f"配置文件未找到: {config_path}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        logger.error(f"配置文件解析错误: {e}")
        sys.exit(1)

# 检查输出目录
def check_output_dir(output_dir):
    """检查输出目录是否存在，不存在则创建"""
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    logger.info(f"输出目录: {output_dir}")

# 保存数据到文件
def save_data_to_file(data: Dict[str, Any], output_dir: str, hour: int, day: int):
    """将数据保存到TXT文件"""
    # 生成文件名
    timestamp = f"{day:02d}_{hour:02d}"
    filename = f"performance_{timestamp}.txt"
    file_path = os.path.join(output_dir, filename)
    
    try:
        # 转换数据为字符串格式
        lines = []
        lines.append(f"=== 性能数据 - 第{day}天第{hour}小时 ===\n")
        
        if "data" in data and data["data"]:
            for i, record in enumerate(data["data"]):
                lines.append(f"记录 {i+1}:")
                for key, value in record.items():
                    lines.append(f"  {key}: {value}")
                lines.append("")
        else:
            lines.append("没有性能数据\n")
        
        # 保存到文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines([line + '\n' for line in lines])
        
        logger.info(f"数据已保存到: {file_path}")
    except Exception as e:
        logger.error(f"保存数据到文件失败: {e}")

# API调用函数
def call_api(api_url: str, endpoint: str, params: Dict[str, Any] = None, retries: int = 3):
    """调用API接口，支持重试"""
    full_url = f"{api_url}{endpoint}"
    headers = {"Content-Type": "application/json"}
    
    for i in range(retries):
        try:
            response = requests.get(full_url, params=params, headers=headers, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"API调用失败 (尝试 {i+1}/{retries}): {e}")
            if i < retries - 1:
                time.sleep(2)  # 等待2秒后重试
    
    return None

# 主处理函数
def main_processing():
    """主处理函数"""
    global current_hour, current_day, calculator
    
    try:
        # 1. 模拟时间增加
        logger.info(f"开始处理第{current_day}天第{current_hour}小时的数据")
        
        # 2. 执行数据处理
        logger.info(f"执行数据处理流程 - 第{current_day}天第{current_hour}小时")
        success = calculator.process_data_by_hour(current_day, current_hour)
        
        if success:
            logger.info(f"数据处理成功 - 第{current_day}天第{current_hour}小时")
            
            # 3. 调用API获取性能数据
            logger.info(f"调用API获取性能数据 - 第{current_day}天第{current_hour}小时")
            api_params = {
                "heat_exchanger_id": None,  # 可以根据需要设置特定管段
                "day": current_day,
                "hour": current_hour
            }
            
            # 调用API获取性能数据
            performance_data = call_api(config["api_url"], "/performance", api_params)
            
            if performance_data and performance_data["status"] == "success":
                logger.info(f"API调用成功，获取到 {performance_data['count']} 条性能数据")
                
                # 4. 保存数据到文件
                save_data_to_file(performance_data, output_dir, current_hour, current_day)
            else:
                logger.error(f"API调用失败或返回错误状态: {performance_data}")
        else:
            logger.error(f"数据处理失败 - 第{current_day}天第{current_hour}小时")
        
        # 5. 更新时间
        current_hour += 1
        if current_hour >= 24:
            current_hour = 0
            current_day += 1
            
        # 取消天数限制，让脚本可以一直运行
        # logger.info("已完成所有天数的数据处理，脚本结束")
        # sys.exit(0)
            
    except Exception as e:
        logger.error(f"主处理函数异常: {e}", exc_info=True)

# 主函数
def main():
    """主函数"""
    global logger, config, output_dir, current_hour, current_day, calculator
    
    # 1. 设置日志
    logger = setup_logging()
    logger.info("启动自动化数据处理脚本")
    
    # 2. 加载配置
    config = load_config()
    logger.info("配置加载成功")
    
    # 3. 初始化变量
    current_hour = config["start_hour"]
    current_day = config["start_day"]
    interval_minutes = config["interval_minutes"]
    output_dir = os.path.join(os.path.dirname(__file__), config["output_dir"])
    
    # 4. 检查输出目录
    check_output_dir(output_dir)
    
    # 5. 初始化计算器
    logger.info("初始化主计算器")
    config_path = os.path.join(os.path.dirname(__file__), 'config.json')
    calculator = MainCalculator(config_path)
    
    # 6. 执行初始处理
    main_processing()
    
    # 7. 设置定时任务
    logger.info(f"设置定时任务，每{interval_minutes}分钟执行一次")
    schedule.every(interval_minutes).minutes.do(main_processing)
    
    # 8. 运行定时任务
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("脚本被手动终止")
    except Exception as e:
        logger.error(f"脚本运行异常: {e}", exc_info=True)
    finally:
        logger.info("脚本结束运行")

if __name__ == "__main__":
    main()
