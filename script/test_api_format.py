#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json

# 测试API接口
url = "http://localhost:8000/performance?day=10&hour=0"

try:
    response = requests.get(url)
    print(f"状态码: {response.status_code}")
    print(f"Content-Type: {response.headers.get('Content-Type')}")
    print(f"\n响应内容:")
    print(response.text)
    
    # 尝试解析JSON
    data = response.json()
    print(f"\n解析后的数据类型: {type(data)}")
    print(f"数据键: {data.keys() if isinstance(data, dict) else 'N/A'}")
    
    if isinstance(data, dict):
        if 'data' in data:
            print(f"data字段类型: {type(data['data'])}")
            print(f"data字段长度: {len(data['data'])}")
            if len(data['data']) > 0:
                print(f"第一条记录: {data['data'][0]}")
    
except Exception as e:
    print(f"错误: {e}")
