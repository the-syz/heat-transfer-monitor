#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
模拟auto_data_processing.py的回调函数调用
"""

import sys
import os
import json
import requests

# 添加backend目录到路径
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend'))
sys.path.insert(0, backend_dir)

# 模拟on_stage1_complete回调函数
def on_stage1_complete(day):
    """Stage1训练完成后的回调函数，统一输出所有相关结果文件"""
    
    output_dir = os.path.join(os.path.dirname(__file__), 'output')
    api_url = "http://localhost:8000"
    
    print(f"Stage1训练完成，开始输出第1天到第{day}天的所有结果文件")
    
    # 遍历所有天数，输出文件
    for output_day in range(1, day + 1):
        for output_hour in range(24):
            # 调用API获取性能数据
            api_params = {
                "heat_exchanger_id": 1,
                "day": output_day,
                "hour": output_hour
            }
            
            full_url = f"{api_url}/performance"
            print(f"API调用: {full_url}, 参数: {api_params}")
            
            try:
                response = requests.get(full_url, params=api_params, timeout=30)
                response.raise_for_status()
                performance_data = response.json()
                print(f"API调用成功，返回状态: {performance_data.get('status')}, 记录数: {performance_data.get('count')}")
                
                if performance_data and performance_data["status"] == "success":
                    print(f"输出第{output_day}天第{output_hour}小时的结果文件")
                    save_data_to_file(performance_data, output_dir, output_hour, output_day)
                else:
                    print(f"获取第{output_day}天第{output_hour}小时的数据失败，跳过")
            except Exception as e:
                print(f"API调用异常: {e}")
    
    print(f"Stage1训练完成，已输出第1天到第{day}天的所有结果文件")

def save_data_to_file(data, output_dir, hour, day):
    """将数据保存到TXT文件"""
    # 生成文件名
    filename = f"day{day}_hour{hour}.txt"
    file_path = os.path.join(output_dir, filename)
    
    try:
        print(f"save_data_to_file调用 - day={day}, hour={hour}")
        print(f"数据类型: {type(data)}")
        print(f"数据内容: {data}")
        
        # 转换数据为字符串格式
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
        
        print(f"数据已保存到: {file_path}")
    except Exception as e:
        print(f"保存数据到文件失败: {e}")
        import traceback
        print(traceback.format_exc())

# 测试：模拟Stage1完成，输出第1天的数据
print("测试：模拟Stage1完成，输出第1天的数据")
on_stage1_complete(1)
print("\n测试完成")
