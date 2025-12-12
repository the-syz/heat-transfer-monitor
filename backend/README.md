# 换热器性能监测后端系统

## 系统概述

本系统是一个基于FastAPI的换热器性能监测后端系统，用于处理和分析换热器运行数据，实现传热系数的预测和性能评估。

## 系统结构

```
backend/
├── calculation/       # 计算模块
│   ├── lmtd_calculator.py          # LMTD法计算
│   ├── nonlinear_regression.py     # 非线性回归计算
│   └── main_calculator.py          # 主计算协调模块
├── db/                # 数据库模块
│   ├── db_connection.py            # 数据库连接管理
│   └── data_loader.py              # 数据加载和处理
├── api/               # API模块
│   └── main.py                     # FastAPI接口定义
├── config/            # 配置模块
│   └── config.json                 # 系统配置文件
├── requirements.txt    # 依赖项列表
└── test_calculator.py  # 测试脚本
```

## 主要功能

### 1. 数据处理
- 从测试数据库读取运行参数
- 计算物理参数（密度、粘度、比热容等）
- 将数据存储到生产数据库

### 2. 传热系数计算
- 使用LMTD法计算K_lmtd
- 使用非线性回归模型预测K值
- 计算管侧传热系数alpha_i
- 计算结垢热阻

### 3. RESTful API接口
- 健康检查
- 数据处理和性能计算
- 参数查询
- 支持CORS跨域请求

## 配置文件说明

`config.json`包含以下配置项：

- `data_directory`: 数据目录
- `result_directory`: 结果目录
- `training_days`: 训练天数
- `max_days`: 最大处理天数
- `history_days`: 历史数据天数
- `optimization_hours`: 优化小时数
- `stage1_error_threshold`: 阶段1误差阈值
- `stage1_history_days`: 阶段1历史天数
- `algorithms`: 支持的算法列表
- `selected_algorithm`: 选定的算法
- `database`: 数据库连接信息
- `geometry_params`: 几何参数

## 数据库结构

### 主要数据表

1. **heat_exchanger**: 换热器基本信息
2. **operation_parameters**: 运行参数
3. **physical_parameters**: 物理参数
4. **performance_parameters**: 性能参数
5. **k_management**: K值管理
6. **model_parameters**: 模型参数

## 安装和运行

### 安装依赖

```bash
pip install -r requirements.txt
```

### 运行API服务

```bash
cd backend/api
python main.py
```

### 访问API文档

```
http://localhost:8000/docs
```

## API接口说明

### 健康检查
- **GET** `/health`: 检查API是否正常运行

### 数据处理
- **POST** `/process-data/{day}/{hour}`: 处理指定时间的数据

### 参数查询
- **GET** `/operation-parameters`: 获取运行参数
- **GET** `/physical-parameters`: 获取物理参数
- **GET** `/k-management`: 获取K_lmtd数据
- **GET** `/performance`: 获取性能数据
- **GET** `/model-parameters`: 获取模型参数
- **GET** `/heat-exchangers`: 获取换热器信息

### 性能计算
- **GET** `/calculate-performance/{day}/{hour}`: 计算指定时间的性能

## 测试

运行测试脚本：

```bash
cd backend
python test_calculator.py
```

## 使用示例

1. 启动API服务
2. 访问API文档
3. 调用`/process-data/{day}/{hour}`接口处理数据
4. 调用`/calculate-performance/{day}/{hour}`接口计算性能
5. 调用查询接口获取计算结果

## 注意事项

1. 确保MySQL数据库服务正在运行
2. 确保数据库结构已经创建
3. 首次运行前，需要配置`config.json`中的数据库连接信息
4. 可以通过API接口逐个小时处理数据，模拟传感器数据的实时采集
5. 系统使用非线性回归算法预测传热系数，需要足够的训练数据

## 技术栈

- FastAPI: RESTful API开发
- MySQL: 数据库存储
- pandas: 数据处理
- numpy: 数值计算
- pyfluids: 流体物性计算
- scipy: 科学计算
- uvicorn: ASGI服务器

## 维护和更新

1. 定期检查数据库连接和数据完整性
2. 根据实际情况调整模型参数
3. 定期更新依赖项
4. 根据需求扩展API接口

## 故障排除

1. 数据库连接失败：检查数据库服务是否运行，连接信息是否正确
2. 数据处理失败：检查数据格式和完整性
3. 计算结果异常：检查模型参数和输入数据
4. API服务无法启动：检查端口是否被占用，依赖项是否安装完整

## 许可证

本系统采用MIT许可证，可自由使用和修改。
