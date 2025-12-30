# 数据库表结构Excel文件说明

本文件夹包含换热器性能监测系统的6个核心数据库表结构定义文件。

## 文件列表

1. **heat_exchanger.xlsx** - 换热器信息表
   - 存储换热器几何参数和基本信息
   - 包含21个字段：id, type, tube_side_fluid, shell_side_fluid, d_i_original, d_o等

2. **operation_parameters.xlsx** - 运行参数表
   - 存储传感器采集的运行数据
   - 包含9个字段：heat_exchanger_id, timestamp, points, side, temperature, pressure等
   - 唯一约束：(heat_exchanger_id, timestamp, points, side)

3. **physical_parameters.xlsx** - 物性参数表
   - 存储计算得到的流体物性参数
   - 包含11个字段：density, viscosity, thermal_conductivity, specific_heat, reynolds, prandtl等
   - 唯一约束：(heat_exchanger_id, timestamp, points, side)

4. **performance_parameters.xlsx** - 性能参数表
   - 存储最终性能计算结果
   - 包含11个字段：K, alpha_i, alpha_o, heat_duty, effectiveness, lmtd等
   - 唯一约束：(heat_exchanger_id, timestamp, points, side)

5. **k_management.xlsx** - 总传热系数管理表
   - 存储LMTD法计算的K_actual和模型预测的K_predicted
   - 包含8个字段：K_LMTD, K_predicted, K_actual等
   - 唯一约束：(heat_exchanger_id, timestamp, points, side)

6. **model_parameters.xlsx** - 模型参数表
   - 存储非线性回归模型参数
   - 包含6个字段：a, p, b等
   - 唯一约束：(heat_exchanger_id, timestamp)

## 表关系说明

所有表通过 `heat_exchanger_id` 外键关联到 `heat_exchanger` 表，确保数据一致性。

## 数据流向

```
operation_parameters (原始运行数据)
     ↓
physical_parameters (物性计算)
     ↓
k_management + performance_parameters (性能计算与预测)
     ↓
model_parameters (模型参数更新)
```

## 生成信息

- 生成时间：2025年12月30日
- 数据来源：系统设计图表说明.md
- 文件格式：Excel (.xlsx)

## 使用说明

1. 每个Excel文件包含一个数据库表的完整结构定义
2. 包含字段名、数据类型、约束、描述和单位信息
3. 可用于数据库建表、文档编写或系统设计评审

---
生成工具：generate_excel_tables.py
