# 换热器性能监测系统 - API接口文档

**文档版本**：1.0  
**更新日期**：2026年1月4日  
**后端版本**：FastAPI 1.0.0  
**基础URL**：`http://localhost:8000` 或实际部署地址

---

## 目录

1. [接口概述](#1-接口概述)
2. [通用约定](#2-通用约定)
3. [认证接口](#3-认证接口)
4. [数据查询接口](#4-数据查询接口)
5. [数据处理接口](#5-数据处理接口)
6. [实时数据接口](#6-实时数据接口)
7. [错误码说明](#7-错误码说明)
8. [数据模型](#8-数据模型)

---

## 1. 接口概述

### 1.1 接口分类

| 类别 | 接口数量 | 主要功能 | 认证要求 |
|------|----------|----------|----------|
| **系统管理** | 1 | 健康检查、状态监控 | 不需要 |
| **数据处理** | 2 | 触发数据处理和性能计算 | 需要 |
| **数据查询** | 6 | 查询各类参数数据 | 需要 |
| **实时推送** | 1 | 实时数据推送（SSE） | 需要 |
| **用户认证** | 1 | 用户登录获取Token | 不需要 |

### 1.2 接口清单

| 序号 | 接口名称 | 方法 | 路径 | 描述 |
|------|----------|------|------|------|
| 1 | 健康检查 | GET | `/health` | 检查API服务状态 |
| 2 | 用户登录 | POST | `/api/auth/login` | 用户登录获取Token |
| 3 | 处理数据 | POST | `/process-data/{day}/{hour}` | 处理指定时间的数据 |
| 4 | 计算性能 | GET | `/calculate-performance/{day}/{hour}` | 计算指定时间的性能 |
| 5 | 换热器列表 | GET | `/heat-exchangers` | 获取所有换热器信息 |
| 6 | 运行参数 | GET | `/operation-parameters` | 获取运行参数数据 |
| 7 | 物理参数 | GET | `/physical-parameters` | 获取物理参数数据 |
| 8 | 性能参数 | GET | `/performance` | 获取性能参数数据 |
| 9 | K值管理 | GET | `/k-management` | 获取K值管理数据 |
| 10 | 模型参数 | GET | `/model-parameters` | 获取模型参数数据 |
| 11 | 实时数据 | SSE | `/realtime-stream` | 实时数据推送流 |

---

## 2. 通用约定

### 2.1 请求头

| 头部字段 | 必选 | 示例值 | 说明 |
|----------|------|--------|------|
| `Content-Type` | 是 | `application/json` | 请求体类型（POST请求） |
| `Authorization` | 是（需认证接口） | `Bearer eyJ0eXAiOiJKV1Qi...` | JWT Token认证 |
| `Accept` | 否 | `application/json` | 期望的响应类型 |

### 2.2 响应格式

#### 成功响应
```json
{
  "status": "success",
  "message": "操作成功描述",
  "data": {} | [],
  "timestamp": "2026-01-04T18:06:00Z"
}
```

#### 错误响应
```json
{
  "status": "error",
  "code": "ERROR_CODE",
  "type": "ErrorType",
  "message": "错误描述信息",
  "timestamp": "2026-01-04T18:06:00Z"
}
```

### 2.3 分页与排序

当前版本接口暂不支持分页和排序，所有查询返回全部匹配数据。

---

## 3. 认证接口

### 3.1 用户登录

**端点**：`POST /api/auth/login`  
**描述**：用户登录获取JWT Token  
**认证**：不需要

#### 请求参数
```json
{
  "username": "string, 用户名",
  "password": "string, 密码"
}
```

#### 响应示例
```json
{
  "status": "success",
  "message": "登录成功",
  "data": {
    "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "user": {
      "id": 1,
      "username": "operator1",
      "role": "operator",
      "permissions": ["view_heat_exchanger_1", "view_heat_exchanger_2"],
      "display_name": "现场操作员A"
    }
  },
  "timestamp": "2026-01-04T18:06:00Z"
}
```

#### 用户角色定义
```typescript
enum UserRole {
  OPERATOR = "operator",      // 现场操作员
  ENGINEER = "engineer",      // 设备工程师
  ADMIN = "admin"            // 系统管理员
}
```

---

## 4. 数据查询接口

### 4.1 获取所有换热器

**端点**：`GET /heat-exchangers`  
**描述**：获取用户有权限访问的所有换热器信息  
**认证**：需要（Bearer Token）

#### 查询参数
无

#### 响应示例
```json
{
  "status": "success",
  "count": 3,
  "data": [
    {
      "id": 1,
      "name": "主反应器换热器",
      "type": "管壳式",
      "tube_side_fluid": "水",
      "shell_side_fluid": "蒸汽",
      "tube_section_count": 12,
      "shell_section_count": 1,
      "health_status": "normal",
      "last_update": "2026-01-04T18:06:00Z"
    },
    {
      "id": 2,
      "name": "辅助换热器A",
      "type": "板式",
      "tube_side_fluid": "水",
      "shell_side_fluid": "水",
      "tube_section_count": 8,
      "shell_section_count": 1,
      "health_status": "warning",
      "last_update": "2026-01-04T17:45:00Z"
    }
  ],
  "timestamp": "2026-01-04T18:06:00Z"
}
```

### 4.2 获取运行参数

**端点**：`GET /operation-parameters`  
**描述**：获取运行参数数据（温度、压力、流速等）  
**认证**：需要（Bearer Token）

#### 查询参数
| 参数名 | 类型 | 必选 | 默认值 | 描述 | 示例 |
|--------|------|------|--------|------|------|
| `heat_exchanger_id` | integer | 否 | 1 | 换热器ID | `1` |
| `day` | integer | 否 | - | 天数（1-31） | `15` |
| `hour` | integer | 否 | - | 小时（0-23） | `8` |

#### 使用示例
```bash
# 获取换热器1第15天第8小时的数据
GET /operation-parameters?heat_exchanger_id=1&day=15&hour=8

# 获取换热器1第15天全天数据
GET /operation-parameters?heat_exchanger_id=1&day=15

# 获取换热器1所有第8小时的数据（所有天）
GET /operation-parameters?heat_exchanger_id=1&hour=8
```

#### 响应示例
```json
{
  "status": "success",
  "count": 24,
  "data": [
    {
      "id": 1,
      "heat_exchanger_id": 1,
      "timestamp": "2022-01-15 08:00:00",
      "points": 1,
      "side": "tube",
      "temperature": 85.3,
      "pressure": 101325,
      "flow_rate": 0.5,
      "velocity": 1.2
    },
    {
      "id": 2,
      "heat_exchanger_id": 1,
      "timestamp": "2022-01-15 08:00:00",
      "points": 1,
      "side": "shell",
      "temperature": 120.5,
      "pressure": 202650,
      "flow_rate": 0.3,
      "velocity": 0.8
    }
    // ... 更多数据
  ],
  "timestamp": "2026-01-04T18:06:00Z"
}
```

### 4.3 获取物理参数

**端点**：`GET /physical-parameters`  
**描述**：获取物理参数数据（密度、粘度、导热系数等）  
**认证**：需要（Bearer Token）

#### 查询参数
| 参数名 | 类型 | 必选 | 默认值 | 描述 |
|--------|------|------|--------|------|
| `heat_exchanger_id` | integer | 否 | 1 | 换热器ID |
| `day` | integer | 否 | - | 天数（1-31） |
| `hour` | integer | 否 | - | 小时（0-23） |

#### 响应字段
```json
{
  "id": 1,
  "heat_exchanger_id": 1,
  "timestamp": "2022-01-15 08:00:00",
  "points": 1,
  "side": "tube",
  "density": 998.2,              // 密度，单位：kg/m³
  "viscosity": 0.001,            // 动力粘度，单位：Pa·s
  "thermal_conductivity": 0.6,   // 导热系数，单位：W/(m·K)
  "specific_heat": 4182,         // 比热容，单位：J/(kg·K)
  "reynolds": 12000,             // 雷诺数，无量纲
  "prandtl": 7.0                 // 普朗特数，无量纲
}
```

### 4.4 获取性能参数

**端点**：`GET /performance`  
**描述**：获取性能参数数据（总传热系数、热负荷、有效度等）  
**认证**：需要（Bearer Token）

#### 查询参数
同运行参数接口

#### 响应字段
```json
{
  "id": 1,
  "heat_exchanger_id": 1,
  "timestamp": "2022-01-15 08:00:00",
  "points": 1,
  "side": "tube",
  "K": 1250.5,                   // 总传热系数，单位：W/(m²·K)
  "alpha_i": 850.2,              // 管侧传热系数，单位：W/(m²·K)
  "alpha_o": 980.3,              // 壳侧传热系数，单位：W/(m²·K)
  "heat_duty": 1500000,          // 热负荷，单位：W
  "effectiveness": 0.85,         // 有效度，无量纲
  "lmtd": 45.2                   // 对数平均温差，单位：°C
}
```

### 4.5 获取K值管理数据

**端点**：`GET /k-management`  
**描述**：获取K值管理数据（LMTD法计算值、预测值、实际值）  
**认证**：需要（Bearer Token）

#### 查询参数
同运行参数接口

#### 响应字段
```json
{
  "id": 1,
  "heat_exchanger_id": 1,
  "timestamp": "2022-01-15 08:00:00",
  "points": 1,
  "side": "tube",
  "K_LMTD": 1200.0,              // LMTD法计算的总传热系数
  "K_predicted": 1250.5,         // 模型预测的总传热系数
  "K_actual": 1248.3             // 实际总传热系数
}
```

### 4.6 获取模型参数

**端点**：`GET /model-parameters`  
**描述**：获取非线性回归模型参数（a, p, b）  
**认证**：需要（Bearer Token）

#### 查询参数
| 参数名 | 类型 | 必选 | 默认值 | 描述 |
|--------|------|------|--------|------|
| `heat_exchanger_id` | integer | 否 | 1 | 换热器ID |
| `day` | integer | 否 | - | 天数（1-365） |

#### 响应字段
```json
{
  "id": 1,
  "heat_exchanger_id": 1,
  "timestamp": "2022-01-15 00:00:00",
  "a": 0.023,                    // 模型参数a
  "p": 0.8,                      // 模型参数p（雷诺数指数）
  "b": 100.0                     // 模型参数b
}
```

---

## 5. 数据处理接口

### 5.1 处理指定时间的数据

**端点**：`POST /process-data/{day}/{hour}`  
**描述**：触发后端处理指定天数和小时的原始数据  
**认证**：需要（Bearer Token）

#### 路径参数
| 参数名 | 类型 | 必选 | 描述 | 示例 |
|--------|------|------|------|------|
| `day` | integer | 是 | 天数（1-31） | `15` |
| `hour` | integer | 是 | 小时（0-23） | `8` |

#### 响应示例
```json
{
  "status": "success",
  "message": "第15天第8小时的数据处理完成",
  "day": 15,
  "hour": 8,
  "timestamp": "2026-01-04T18:06:00Z"
}
```

### 5.2 计算指定时间的性能

**端点**：`GET /calculate-performance/{day}/{hour}`  
**描述**：触发性能计算，包括非线性回归预测  
**认证**：需要（Bearer Token）

#### 路径参数
同处理数据接口

#### 响应示例
```json
{
  "status": "success",
  "message": "第15天第8小时的性能计算完成",
  "day": 15,
  "hour": 8,
  "timestamp": "2026-01-04T18:06:00Z"
}
```

---

## 6. 实时数据接口

### 6.1 实时数据推送（SSE）

**端点**：`GET /realtime-stream`  
**描述**：服务器推送事件（SSE）接口，用于实时数据推送  
**认证**：需要（Bearer Token）  
**Content-Type**：`text/event-stream`

#### 查询参数
| 参数名 | 类型 | 必选 | 默认值 | 描述 |
|--------|------|------|--------|------|
| `heat_exchanger_id` | integer | 否 | 1 | 换热器ID |

#### 连接示例
```javascript
// 前端连接示例
const eventSource = new EventSource('/realtime-stream?heat_exchanger_id=1', {
  headers: {
    'Authorization': 'Bearer ' + token
  }
});

eventSource.addEventListener('parameters_update', (event) => {
  const data = JSON.parse(event.data);
  // 更新页面数据
});

eventSource.addEventListener('alert_new', (event) => {
  const alert = JSON.parse(event.data);
  // 显示新报警
});
```

#### 事件类型

| 事件类型 | 触发条件 | 数据格式 |
|----------|----------|----------|
| `parameters_update` | 运行参数更新（5-10秒间隔） | 运行参数对象 |
| `performance_update` | 性能参数更新（计算完成后） | 性能参数对象 |
| `alert_new` | 新报警产生 | 报警信息对象 |
| `system_status` | 系统状态变化 | 状态信息对象 |

#### 事件数据示例
```javascript
// parameters_update 事件
event: parameters_update
data: {
  "heat_exchanger_id": 1,
  "timestamp": "2026-01-04T18:06:00Z",
  "data": {
    "points": 1,
    "side": "tube",
    "temperature": 85.3,
    "pressure": 101325,
    "flow_rate": 0.5,
    "velocity": 1.2
  }
}

// alert_new 事件
event: alert_new
data: {
  "id": "alert_001",
  "level": "warning", // warning, error, critical
  "timestamp": "2026-01-04T18:06:00Z",
  "heat_exchanger_id": 1,
  "points": 1,
  "side": "tube",
  "type": "temperature_high",
  "message": "温度超过阈值：85.3°C > 80.0°C",
  "value": 85.3,
  "threshold": 80.0
}
```

#### 重连机制
- 连接断开时自动尝试重新连接
- 使用指数退避策略：1秒, 2秒, 4秒, 8秒, 最大30秒
- 重连超过10次后提示用户检查网络

---

## 7. 错误码说明

### 7.1 HTTP状态码

| 状态码 | 含义 | 常见场景 |
|--------|------|----------|
| `200` | 成功 | 查询成功、处理完成 |
| `400` | 请求错误 | 参数验证失败、格式错误 |
| `401` | 未认证 | Token缺失、无效或过期 |
| `403` | 禁止访问 | 权限不足 |
| `404` | 未找到 | 资源不存在 |
| `500` | 服务器错误 | 内部处理异常 |

### 7.2 业务错误码

| 错误码 | 类型 | 描述 | 解决方案 |
|--------|------|------|----------|
| `INVALID_PARAMETERS` | BadRequest | 参数验证失败 | 检查参数格式和范围 |
| `AUTH_REQUIRED` | Unauthorized | 需要认证 | 提供有效的Token |
| `PERMISSION_DENIED` | Forbidden | 权限不足 | 联系管理员分配权限 |
| `RESOURCE_NOT_FOUND` | NotFound | 资源不存在 | 检查资源ID是否正确 |
| `DATA_PROCESSING_FAILED` | InternalServerError | 数据处理失败 | 检查数据源和后端日志 |
| `PERFORMANCE_CALCULATION_FAILED` | InternalServerError | 性能计算失败 | 检查模型参数和数据 |
| `DATABASE_ERROR` | InternalServerError | 数据库操作失败 | 检查数据库连接和状态 |
| `INTERNAL_SERVER_ERROR` | InternalServerError | 服务器内部错误 | 联系系统管理员 |

### 7.3 错误响应示例
```json
{
  "status": "error",
  "code": "INVALID_PARAMETERS",
  "type": "BadRequest",
  "message": "day参数必须在1-31之间",
  "timestamp": "2026-01-04T18:06:00Z"
}
```

---

## 8. 数据模型

### 8.1 换热器信息 (HeatExchanger)
```typescript
interface HeatExchanger {
  id: number;                    // 主键，换热器编号
  name: string;                  // 换热器名称
  type: string;                  // 换热器种类
  tube_side_fluid: string;       // 管侧工质
  shell_side_fluid: string;      // 壳侧工质
  tube_section_count: number;    // 管侧分段数
  shell_section_count: number;   // 壳侧分段数
  health_status: 'normal' | 'warning' | 'fault';  // 健康状态
  last_update: string;           // 最后更新时间
}
```

### 8.2 运行参数 (OperationParameters)
```typescript
interface OperationParameters {
  id: number;                    // 主键
  heat_exchanger_id: number;     // 外键，换热器ID
  timestamp: string;             // 时间戳
  points: number;                // 测量点（整型）
  side: 'tube' | 'shell';        // 侧标识
  temperature: number;           // 温度，°C
  pressure: number;              // 压力，Pa
  flow_rate: number;             // 流量，m³/s
  velocity: number;              // 流速，m/s
}
```

### 8.3 性能参数 (PerformanceParameters)
```typescript
interface PerformanceParameters {
  id: number;                    // 主键
  heat_exchanger_id: number;     // 外键，换热器ID
  timestamp: string;             // 时间戳
  points: number;                // 测量点（整型）
  side: 'tube' | 'shell';        // 侧标识
  K: number;                     // 总传热系数，W/(m²·K)
  alpha_i: number;               // 管侧传热系数，W/(m²·K)
  alpha_o: number;               // 壳侧传热系数，W/(m²·K)
  heat_duty: number;             // 热负荷，W
  effectiveness: number;         // 有效度，无量纲
  lmtd: number;                  // 对数平均温差，°C
}
```

### 8.4 用户信息 (User)
```typescript
interface User {
  id: number;                    // 用户ID
  username: string;              // 用户名
  role: 'operator' | 'engineer' | 'admin';  // 角色
  permissions: string[];         // 权限列表
  display_name: string;          // 显示名称
  assigned_heat_exchangers: number[];  // 负责的换热器ID列表
}
```

### 8.5 报警信息 (Alert)
```typescript
interface Alert {
  id: string;                    // 报警ID
  level: 'warning' | 'error' | 'critical';  // 报警级别
  timestamp: string;             // 发生时间
  heat_exchanger_id: number;     // 换热器ID
  points: number;                // 测量点
  side: 'tube' | 'shell';        // 侧标识
  type: string;                  // 报警类型
  message: string;               // 报警描述
  value: number;                 // 实际值
  threshold: number;             // 阈值
  status: 'new' | 'acknowledged' | 'resolved';  // 状态
}
```

---

## 附录

### A. 接口测试工具

#### 使用curl测试
```bash
# 测试健康检查
curl -X GET "http://localhost:8000/health"

# 测试获取运行参数（带Token）
curl -X GET "http://localhost:8000/operation-parameters?day=15&hour=8" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"

# 测试SSE连接
curl -N "http://localhost:8000/realtime-stream" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Accept: text/event-stream"
```

#### 使用Postman测试
1. 导入Postman集合（提供JSON文件）
2. 设置环境变量：`base_url`, `token`
3. 运行接口测试

### B. 前端集成示例

```typescript
// API服务封装示例
class HeatExchangerAPI {
  private baseURL: string;
  private token: string | null;

  constructor(baseURL: string) {
    this.baseURL = baseURL;
    this.token = localStorage.getItem('token');
  }

  // 登录方法
  async login(username: string, password: string): Promise<User> {
    const response = await fetch(`${this.baseURL}/api/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password })
    });
    
    const result = await response.json();
    if (result.status === 'success') {
      this.token = result.data.token;
      localStorage.setItem('token', this.token);
      return result.data.user;
    } else {
      throw new Error(result.message);
    }
  }

  // 获取换热器列表
  async getHeatExchangers(): Promise<HeatExchanger[]> {
    const response = await fetch(`${this.baseURL}/heat-exchangers`, {
      headers: this.getAuthHeaders()
    });
    
    const result = await response.json();
    return result.data;
  }

  // SSE连接
  connectRealtimeStream(heatExchangerId: number): EventSource {
    return new EventSource(
      `${this.baseURL}/realtime-stream?heat_exchanger_id=${heatExchangerId}`,
      { headers: this.getAuthHeaders() }
    );
  }

  private getAuthHeaders(): HeadersInit {
    const headers: HeadersInit = {
      'Accept': 'application/json'
    };
    
    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }
    
    return headers;
  }
}
```

### C. 版本历史

| 版本 | 日期 | 变更描述 |
|------|------|----------|
| 1.0 | 2026-01-04 | 初始版本，基于现有后端API |

---

**文档状态**：✅ 审核通过  
**维护责任**：后端开发团队负责接口维护，前端团队负责集成

*本文档将随接口变更而更新，请在使用前确认版本一致性。*