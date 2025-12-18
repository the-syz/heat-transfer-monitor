# 数据处理与API调用自动化脚本

## 功能说明

该脚本实现了换热器性能监测系统的数据自动处理和API调用功能，主要包括以下内容：

1. **数据模拟与读取**：从`..._test`数据库中读取运行参数、物理参数和性能参数
2. **定时处理机制**：每间隔1分钟，模拟增加1小时的时间来读取该小时段内的全部数据
3. **数据计算流程**：对每个小时段的完整数据执行预设的计算流程
4. **API接口调用**：在完成每小时数据处理后，调用指定API接口获取特定管段的指定参数
5. **文件输出管理**：将每个小时通过API获取到的数据以TXT格式保存至脚本所在目录的`output`文件夹中，文件名包含对应的小时时间戳

## 脚本结构

```
auto_data_processing.py
├── Config类：管理脚本的各种配置参数
├── DatabaseHandler类：负责与数据库交互
├── APIClient类：负责与API交互
├── DataProcessor类：负责执行计算流程
├── OutputManager类：负责保存结果文件
└── AutoProcessor类：协调各个组件完成自动化任务
```

## 配置说明

### 配置文件路径
```python
# 默认配置文件路径
backend/config/config.json
```

### 可配置参数

在`Config`类中可以配置以下参数：

| 参数名 | 描述 | 默认值 |
| ------ | ---- | ------ |
| `api_base_url` | API基础URL | `http://localhost:8000` |
| `api_timeout` | API请求超时时间（秒） | `30` |
| `time_interval` | 处理时间间隔（秒） | `60` |
| `start_day` | 开始处理的天数 | `1` |
| `start_hour` | 开始处理的小时 | `0` |
| `output_folder` | 输出文件夹路径 | `output` |
| `target_section_id` | 目标管段ID | `1` |

## 使用方法

### 1. 启动API服务

首先需要启动换热器性能监测系统的API服务：

```bash
cd backend/api
python main.py
```

### 2. 启动自动化脚本

```bash
python script/auto_data_processing.py
```

### 3. 查看输出结果

处理结果将保存在`script/output`文件夹中，文件名格式为：

```
section_params_day{day}_hour{hour}_{timestamp}.txt
```

## 日志记录

脚本会生成日志文件`auto_data_processing.log`，记录脚本的运行情况和错误信息。

## 错误处理

脚本包含完善的错误处理机制，能够处理以下情况：

1. 数据库连接失败
2. API调用失败
3. 数据处理错误
4. 文件保存失败

## 依赖项

- Python 3.6+
- requests
- json
- os
- sys
- time
- logging
- datetime
- mysql-connector-python

## 注意事项

1. 确保在启动脚本前，API服务已经正常运行
2. 确保数据库服务已经启动，并且配置文件中的数据库连接信息正确
3. 脚本会自动创建`output`文件夹，无需手动创建
4. 可以通过修改`Config`类中的参数来调整脚本的运行行为
5. 按`Ctrl+C`可以停止脚本的运行