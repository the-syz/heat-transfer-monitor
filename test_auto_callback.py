#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试auto_data_processing.py的回调函数
"""

import sys
import os
import json

# 添加backend目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'backend')))

import requests

# 加载配置
config_path = os.path.join(os.path.dirname(__file__), 'script', 'config.json')
with open(config_path, 'r', encoding='utf-8') as f:
    config = json.load(f)

# 输出目录
output_dir = os.path.join(os.path.dirname(__file__), config["output_dir"])

def save_data_to_file(data, output_dir, hour, day):
    """将数据保存到文件"""
    try:
        # 创建文件名
        filename = f"day{day}_hour{hour}.txt"
        file_path = os.path.join(output_dir, filename)
        
        # 构建文件内容
        lines = []
        lines.append(f"第{day}天第{hour}小时性能数据")
        lines.append("=" * 50)
        
        if data and "data" in data:
            lines.append(f"数据条数: {data.get('count', 0)}")
            lines.append("")
            
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
        
        print(f"数据已保存到: {file_path}")
        return True
    except Exception as e:
        print(f"保存数据到文件失败: {e}")
        return False

def call_api(api_url: str, endpoint: str, params: dict = None, retries: int = 3):
    """调用API接口，支持重试"""
    full_url = f"{api_url}{endpoint}"
    headers = {"Content-Type": "application/json"}
    
    for i in range(retries):
        try:
            print(f"API调用: {full_url}, 参数: {params}")
            response = requests.get(full_url, params=params, headers=headers, timeout=30)
            response.raise_for_status()
            data = response.json()
            print(f"API调用成功，返回状态: {data.get('status')}")
            return data
        except requests.exceptions.RequestException as e:
            print(f"API调用失败 (尝试 {i+1}/{retries}): {e}")
            if i < retries - 1:
                print(f"{i+1}秒后重试...")
                import time
                time.sleep(i+1)  # 指数退避重试策略
    
    print(f"API调用失败，已达到最大重试次数 {retries}")
    return None

def test_stage1_callback():
    """测试Stage1完成回调函数"""
    print("=== 测试Stage1完成回调函数 ===")
    
    # 检查输出目录
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"创建输出目录: {output_dir}")
    
    # 测试输出第1天第0小时的数据
    print("\n测试输出第1天第0小时的数据...")
    api_params = {
        "heat_exchanger_id": 1,
        "day": 1,
        "hour": 0
    }
    
    performance_data = call_api(config["api_url"], "/performance", api_params)
    
    if performance_data and performance_data["status"] == "success":
        print(f"输出第1天第0小时的结果文件")
        save_data_to_file(performance_data, output_dir, 0, 1)
    else:
        print(f"获取第1天第0小时的数据失败")
    
    # 检查输出目录中的文件
    print("\n=== 输出目录中的文件 ===")
    files = os.listdir(output_dir)
    print(f"文件数量: {len(files)}")
    for file in files:
        print(f"  {file}")

if __name__ == "__main__":
    test_stage1_callback()
