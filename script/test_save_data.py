#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import json
import requests

# 添加backend目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))

# 导入backend模块
from db.db_connection import DatabaseConnection

# 配置
config = {
    "api_url": "http://localhost:8000",
    "output_dir": os.path.join(os.path.dirname(__file__), 'output')
}

def save_data_to_file(data, output_dir, hour, day):
    """将数据保存到TXT文件"""
    filename = f"day{day}_hour{hour}.txt"
    file_path = os.path.join(output_dir, filename)
    
    print(f"\n=== save_data_to_file调用 ===")
    print(f"day={day}, hour={hour}")
    print(f"数据类型: {type(data)}")
    print(f"数据内容: {data}")
    
    lines = []
    lines.append(f"=== 性能数据 - 第{day}天第{hour}小时 ===\n")
    
    if "data" in data and data["data"]:
        print(f"找到data字段,包含{len(data['data'])}条记录")
        for i, record in enumerate(data["data"]):
            lines.append(f"记录 {i+1}:")
            for key, value in record.items():
                lines.append(f"  {key}: {value}")
            lines.append("")
    else:
        print(f"没有找到data字段或data为空: 'data' in data = {'data' in data}, data.get('data') = {data.get('data')}")
        lines.append("没有性能数据\n")
    
    # 保存到文件
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines([line + '\n' for line in lines])
    
    print(f"数据已保存到: {file_path}\n")

def call_api(api_url, endpoint, params):
    """调用API接口"""
    full_url = f"{api_url}{endpoint}"
    print(f"\n=== API调用 ===")
    print(f"URL: {full_url}")
    print(f"参数: {params}")
    
    try:
        response = requests.get(full_url, params=params, headers={"Content-Type": "application/json"}, timeout=30)
        response.raise_for_status()
        data = response.json()
        print(f"API调用成功")
        print(f"返回数据类型: {type(data)}")
        print(f"返回数据键: {data.keys() if isinstance(data, dict) else 'N/A'}")
        return data
    except Exception as e:
        print(f"API调用失败: {e}")
        return None

# 测试第10天第0小时
print("=" * 60)
print("测试: 第10天第0小时")
print("=" * 60)

api_params = {
    "heat_exchanger_id": 1,
    "day": 10,
    "hour": 0
}

performance_data = call_api(config["api_url"], "/performance", api_params)

if performance_data and performance_data.get("status") == "success":
    print(f"获取数据成功,状态: {performance_data.get('status')}")
    save_data_to_file(performance_data, config["output_dir"], 0, 10)
else:
    print(f"获取数据失败")

print("\n" + "=" * 60)
print("测试完成")
print("=" * 60)
