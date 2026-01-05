# 第二阶段：API服务模块 - 详细任务分解

**阶段目标**：封装统一的HTTP请求工具，实现换热器相关API接口和实时数据SSE连接  
**预估工期**：5人日  
**关键产出**：完整可用的API服务层，支持HTTP请求、错误处理和实时数据推送

---

## 任务清单

### T2.1.1 封装HTTP请求工具

#### 任务描述
1. **封装Axios实例**：
   - 创建统一的Axios实例，配置基础选项
   - 实现请求/响应拦截器
   - 配置超时和重试机制

2. **实现拦截器功能**：
   - 请求拦截器：自动注入Authorization Token
   - 响应拦截器：统一错误处理和状态码处理
   - Token过期自动刷新机制

3. **实现请求工具函数**：
   - 封装GET、POST、PUT、DELETE等方法
   - 实现文件上传下载支持
   - 添加请求取消功能

#### 技术细节与实现步骤

**步骤1：创建请求工具文件**
```javascript
// src/utils/request.js
import axios from 'axios'
import { useAuthStore } from '@/stores/auth'
import router from '@/router'

// 创建axios实例
const request = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  timeout: 10000, // 10秒超时
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
request.interceptors.request.use(
  (config) => {
    // 从store获取token
    const authStore = useAuthStore()
    const token = authStore.token
    
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    
    // 添加请求时间戳（防缓存）
    if (config.method === 'get') {
      config.params = {
        ...config.params,
        _t: Date.now()
      }
    }
    
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
request.interceptors.response.use(
  (response) => {
    // 统一处理成功响应
    return response.data
  },
  async (error) => {
    const originalRequest = error.config
    
    // 处理401错误（Token过期）
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true
      
      try {
        // 尝试刷新Token
        const authStore = useAuthStore()
        await authStore.refreshToken()
        
        // 更新请求头中的Token
        const newToken = authStore.token
        originalRequest.headers.Authorization = `Bearer ${newToken}`
        
        // 重新发送原始请求
        return request(originalRequest)
      } catch (refreshError) {
        // 刷新失败，跳转到登录页
        authStore.logout()
        router.push('/login')
        return Promise.reject(refreshError)
      }
    }
    
    // 其他错误处理
    const errorMessage = getErrorMessage(error)
    showErrorToast(errorMessage)
    
    return Promise.reject(error)
  }
)

// 错误消息映射
function getErrorMessage(error) {
  if (error.response) {
    // 服务器返回错误
    const { status, data } = error.response
    
    switch (status) {
      case 400:
        return data.message || '请求参数错误'
      case 403:
        return '权限不足，无法访问此资源'
      case 404:
        return '请求的资源不存在'
      case 500:
        return '服务器内部错误，请稍后重试'
      case 502:
        return '网关错误，请检查网络连接'
      case 503:
        return '服务暂时不可用，请稍后重试'
      default:
        return data.message || `请求失败 (${status})`
    }
  } else if (error.request) {
    // 请求发送但无响应
    return '网络连接失败，请检查网络设置'
  } else {
    // 请求配置错误
    return error.message || '请求发送失败'
  }
}

// 显示错误提示
function showErrorToast(message) {
  // 使用Element Plus的消息提示
  import('element-plus').then(({ ElMessage }) => {
    ElMessage.error(message)
  })
}

// 请求重试配置
const retryConfig = {
  retries: 3, // 最大重试次数
  retryDelay: 1000, // 重试延迟（毫秒）
  retryCondition: (error) => {
    // 只在网络错误或5xx错误时重试
    return !error.response || error.response.status >= 500
  }
}

// 封装请求方法
export const http = {
  get: (url, params = {}, config = {}) => {
    return request.get(url, { params, ...config })
  },
  
  post: (url, data = {}, config = {}) => {
    return request.post(url, data, config)
  },
  
  put: (url, data = {}, config = {}) => {
    return request.put(url, data, config)
  },
  
  delete: (url, config = {}) => {
    return request.delete(url, config)
  },
  
  upload: (url, file, config = {}) => {
    const formData = new FormData()
    formData.append('file', file)
    
    return request.post(url, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      },
      ...config
    })
  },
  
  download: (url, params = {}, filename = 'download') => {
    return request.get(url, {
      params,
      responseType: 'blob'
    }).then(response => {
      // 创建下载链接
      const blob = new Blob([response])
      const downloadUrl = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = downloadUrl
      link.download = filename
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(downloadUrl)
    })
  }
}

// 请求取消功能
export const createCancelToken = () => {
  return axios.CancelToken.source()
}

export default request
```

**步骤2：配置环境变量支持**
```javascript
// src/utils/env.js
/**
 * 环境变量管理工具
 */

export const env = {
  // API基础地址
  apiBaseUrl: import.meta.env.VITE_API_BASE_URL,
  
  // 应用标题
  appTitle: import.meta.env.VITE_APP_TITLE,
  
  // 调试模式
  isDebug: import.meta.env.VITE_DEBUG === 'true',
  
  // 构建时间
  buildTime: import.meta.env.VITE_BUILD_TIME,
  
  // CDN地址
  cdnUrl: import.meta.env.VITE_CDN_URL,
  
  // 获取所有环境变量
  getAll() {
    return {
      apiBaseUrl: this.apiBaseUrl,
      appTitle: this.appTitle,
      isDebug: this.isDebug,
      buildTime: this.buildTime,
      cdnUrl: this.cdnUrl
    }
  },
  
  // 验证必需的环境变量
  validate() {
    const required = ['VITE_API_BASE_URL']
    const missing = required.filter(key => !import.meta.env[key])
    
    if (missing.length > 0) {
      console.error(`缺少必需的环境变量: ${missing.join(', ')}`)
      return false
    }
    
    return true
  }
}

// 在应用启动时验证环境变量
if (import.meta.env.DEV) {
  env.validate()
}
```

**步骤3：创建API服务层**
```javascript
// src/api/index.js
/**
 * API服务统一入口
 */

// 导出所有API模块
export * from './heat-exchanger'
export * from './auth'
export * from './realtime'
export * from './alert'

// 导出请求工具
export { http, createCancelToken } from '@/utils/request'
```

#### 验收条件
1. **请求工具验证**：
   - Axios实例能成功发送HTTP请求
   - 请求拦截器能正确注入Token
   - 响应拦截器能统一处理错误
   - Token过期能自动刷新

2. **错误处理验证**：
   - 网络错误能正确显示提示
   - 服务器错误能正确映射错误信息
   - 401错误能触发重新登录流程

3. **功能完整性验证**：
   - GET、POST、PUT、DELETE方法工作正常
   - 文件上传下载功能可用
   - 请求取消功能正常

4. **环境变量验证**：
   - 环境变量能正确加载
   - 必需的环境变量验证通过
   - 开发和生产环境配置正确

#### 产出物清单
- ✓ src/utils/request.js（HTTP请求工具）
- ✓ src/utils/env.js（环境变量管理）
- ✓ src/api/index.js（API统一入口）
- ✓ 完整的错误处理机制
- ✓ Token自动刷新功能
- ✓ 请求重试和取消功能

---

### T2.1.2 实现换热器相关API接口

#### 任务描述
1. **封装换热器数据接口**：
   - 换热器列表查询接口
   - 换热器详情查询接口
   - 换热器运行参数接口

2. **封装性能参数接口**：
   - 传热系数K值查询接口
   - 污垢热阻查询接口
   - 性能趋势数据接口

3. **封装数据处理接口**：
   - 数据重新处理接口
   - 数据导出接口
   - 数据统计接口

#### 技术细节与实现步骤

**步骤1：创建换热器API模块**
```javascript
// src/api/heat-exchanger.js
import { http } from '@/utils/request'

/**
 * 换热器相关API接口
 */
export const heatExchangerAPI = {
  /**
   * 获取换热器列表
   * @param {Object} params - 查询参数
   * @returns {Promise} 换热器列表
   */
  getHeatExchangers(params = {}) {
    return http.get('/api/heat-exchangers', params)
  },
  
  /**
   * 获取换热器详情
   * @param {string|number} id - 换热器ID
   * @returns {Promise} 换热器详情
   */
  getHeatExchangerDetail(id) {
    return http.get(`/api/heat-exchangers/${id}`)
  },
  
  /**
   * 获取换热器运行参数
   * @param {string|number} id - 换热器ID
   * @param {Object} params - 查询参数
   * @returns {Promise} 运行参数
   */
  getOperationParameters(id, params = {}) {
    return http.get(`/api/heat-exchangers/${id}/operation-parameters`, params)
  },
  
  /**
   * 获取换热器物理参数
   * @param {string|number} id - 换热器ID
   * @returns {Promise} 物理参数
   */
  getPhysicalParameters(id) {
    return http.get(`/api/heat-exchangers/${id}/physical-parameters`)
  },
  
  /**
   * 获取换热器性能参数
   * @param {string|number} id - 换热器ID
   * @param {Object} params - 查询参数
   * @returns {Promise} 性能参数
   */
  getPerformanceParameters(id, params = {}) {
    return http.get(`/api/heat-exchangers/${id}/performance`, params)
  },
  
  /**
   * 获取管段列表
   * @param {string|number} id - 换热器ID
   * @param {string} side - 侧别：'tube' 或 'shell'
   * @returns {Promise} 管段列表
   */
  getSections(id, side = 'tube') {
    return http.get(`/api/heat-exchangers/${id}/sections`, { side })
  },
  
  /**
   * 获取管段详情
   * @param {string|number} heatExchangerId - 换热器ID
   * @param {string|number} sectionNumber - 管段编号
   * @returns {Promise} 管段详情
   */
  getSectionDetail(heatExchangerId, sectionNumber) {
    return http.get(`/api/heat-exchangers/${heatExchangerId}/sections/${sectionNumber}`)
  },
  
  /**
   * 获取传热系数K值
   * @param {string|number} id - 换热器ID
   * @param {Object} params - 查询参数
   * @returns {Promise} K值数据
   */
  getKValues(id, params = {}) {
    return http.get(`/api/heat-exchangers/${id}/k-values`, params)
  },
  
  /**
   * 获取污垢热阻
   * @param {string|number} id - 换热器ID
   * @param {Object} params - 查询参数
   * @returns {Promise} 污垢热阻数据
   */
  getFoulingResistance(id, params = {}) {
    return http.get(`/api/heat-exchangers/${id}/fouling-resistance`, params)
  },
  
  /**
   * 获取性能趋势数据
   * @param {string|number} id - 换热器ID
   * @param {string} param - 参数名称
   * @param {Object} params - 时间范围参数
   * @returns {Promise} 趋势数据
   */
  getPerformanceTrend(id, param, params = {}) {
    return http.get(`/api/heat-exchangers/${id}/performance-trend/${param}`, params)
  },
  
  /**
   * 重新处理数据
   * @param {string|number} id - 换热器ID
   * @param {Object} data - 处理参数
   * @returns {Promise} 处理结果
   */
  reprocessData(id, data = {}) {
    return http.post(`/api/heat-exchangers/${id}/reprocess`, data)
  },
  
  /**
   * 导出数据
   * @param {string|number} id - 换热器ID
   * @param {Object} params - 导出参数
   * @param {string} filename - 导出文件名
   * @returns {Promise} 下载结果
   */
  exportData(id, params = {}, filename = 'heat-exchanger-data.csv') {
    return http.download(`/api/heat-exchangers/${id}/export`, params, filename)
  },
  
  /**
   * 获取数据统计
   * @param {string|number} id - 换热器ID
   * @returns {Promise} 统计数据
   */
  getStatistics(id) {
    return http.get(`/api/heat-exchangers/${id}/statistics`)
  },
  
  /**
   * 获取健康状态
   * @param {string|number} id - 换热器ID
   * @returns {Promise} 健康状态
   */
  getHealthStatus(id) {
    return http.get(`/api/heat-exchangers/${id}/health-status`)
  },
  
  /**
   * 获取报警统计
   * @param {string|number} id - 换热器ID
   * @returns {Promise} 报警统计
   */
  getAlertStatistics(id) {
    return http.get(`/api/heat-exchangers/${id}/alert-statistics`)
  }
}

// 默认导出
export default heatExchangerAPI
```

**步骤2：创建数据模型**
```javascript
// src/models/heat-exchanger.js
/**
 * 换热器数据模型
 */

export class HeatExchanger {
  constructor(data) {
    this.id = data.id
    this.name = data.name || ''
    this.type = data.type || ''
    this.tubeSideFluid = data.tube_side_fluid || ''
    this.shellSideFluid = data.shell_side_fluid || ''
    this.tubeSectionCount = data.tube_section_count || 0
    this.shellSectionCount = data.shell_section_count || 0
    this.healthStatus = data.health_status || 'normal'
    this.lastUpdate = data.last_update ? new Date(data.last_update) : new Date()
    this.description = data.description || ''
    this.location = data.location || ''
    this.manufacturer = data.manufacturer || ''
    this.installationDate = data.installation_date ? new Date(data.installation_date) : null
  }
  
  getHealthColor() {
    const colors = {
      normal: '#4caf50',
      warning: '#ff9800',
      fault: '#f44336',
      offline: '#9e9e9e'
    }
    return colors[this.healthStatus] || '#9e9e9e'
  }
  
  getHealthText() {
    const texts = {
      normal: '正常',
      warning: '警告',
      fault: '故障',
      offline: '离线'
    }
    return texts[this.healthStatus] || '未知'
  }
  
  isOnline() {
    return this.healthStatus !== 'offline'
  }
  
  needsAttention() {
    return this.healthStatus === 'warning' || this.healthStatus === 'fault'
  }
}

export class OperationParameter {
  constructor(data) {
    this.id = data.id
    this.heatExchangerId = data.heat_exchanger_id
    this.timestamp = data.timestamp ? new Date(data.timestamp) : new Date()
    this.tubeInletTemp = data.tube_inlet_temp || 0
    this.tubeOutletTemp = data.tube_outlet_temp || 0
    this.shellInletTemp = data.shell_inlet_temp || 0
    this.shellOutletTemp = data.shell_outlet_temp || 0
    this.tubeFlowRate = data.tube_flow_rate || 0
    this.shellFlowRate = data.shell_flow_rate || 0
    this.tubePressure = data.tube_pressure || 0
    this.shellPressure = data.shell_pressure || 0
    this.ambientTemp = data.ambient_temp || 0
  }
  
  getTemperatureDifference(side = 'tube') {
    if (side === 'tube') {
      return this.tubeInletTemp - this.tubeOutletTemp
    } else {
      return this.shellInletTemp - this.shellOutletTemp
    }
  }
  
  getFlowRate(side = 'tube') {
    return side === 'tube' ? this.tubeFlowRate : this.shellFlowRate
  }
  
  getPressure(side = 'tube') {
    return side === 'tube' ? this.tubePressure : this.shellPressure
  }
}

export class PerformanceParameter {
  constructor(data) {
    this.id = data.id
    this.heatExchangerId = data.heat_exchanger_id
    this.sectionNumber = data.section_number || 0
    this.timestamp = data.timestamp ? new Date(data.timestamp) : new Date()
    this.kValue = data.k_value || 0
    this.foulingResistance = data.fouling_resistance || 0
    this.heatDuty = data.heat_duty || 0
    this.effectiveness = data.effectiveness || 0
    this.ntu = data.ntu || 0
    this.reynoldsNumber = data.reynolds_number || 0
    this.prandtlNumber = data.prandtl_number || 0
  }
  
  getKValueTrend(history = []) {
    if (history.length === 0) return 'stable'
    
    const recentValues = history.slice(-10).map(item => item.kValue)
    const current = this.kValue
    const average = recentValues.reduce((a, b) => a + b, 0) / recentValues.length
    
    if (current > average * 1.1) return 'improving'
    if (current < average * 0.9) return 'declining'
    return 'stable'
  }
  
  isFoulingCritical(threshold = 0.0005) {
    return this.foulingResistance > threshold
  }
}
```

**步骤3：创建API响应处理工具**
```javascript
// src/utils/api-response.js
/**
 * API响应处理工具
 */

/**
 * 处理API响应，转换为模型对象
 * @param {Object} response - API响应数据
 * @param {Function} ModelClass - 模型类
 * @returns {Object|Array} 转换后的数据
 */
export function processApiResponse(response, ModelClass = null) {
  if (!response) return null
  
  // 如果是数组
  if (Array.isArray(response)) {
    return ModelClass ? response.map(item => new ModelClass(item)) : response
  }
  
  // 如果是分页响应
  if (response.data && Array.isArray(response.data)) {
    const processedData = ModelClass 
      ? response.data.map(item => new ModelClass(item))
      : response.data
    
    return {
      data: processedData,
      total: response.total || 0,
      page: response.page || 1,
      pageSize: response.pageSize || 10,
      totalPages: response.totalPages || 1
    }
  }
  
  // 如果是单个对象
  return ModelClass ? new ModelClass(response) : response
}

/**
 * 创建查询参数
 * @param {Object} options - 查询选项
 * @returns {Object} 查询参数对象
 */
export function createQueryParams(options = {}) {
  const {
    page = 1,
    pageSize = 10,
    sortBy = '',
    sortOrder = 'desc',
    filters = {},
    timeRange = {},
    search = ''
  } = options
  
  const params = {
    page,
    page_size: pageSize
  }
  
  // 排序参数
  if (sortBy) {
    params.sort_by = sortBy
    params.sort_order = sortOrder
  }
  
  // 搜索参数
  if (search) {
    params.search = search
  }
  
  // 时间范围参数
  if (timeRange.start || timeRange.end) {
    if (timeRange.start) {
      params.start_time = timeRange.start.toISOString()
    }
    if (timeRange.end) {
      params.end_time = timeRange.end.toISOString()
    }
  }
  
  // 过滤参数
  Object.entries(filters).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') {
      params[`filter_${key}`] = value
    }
  })
  
  return params
}

/**
 * 处理API错误
 * @param {Error} error - API错误
 * @param {string} context - 错误上下文
 * @returns {string} 用户友好的错误消息
 */
export function handleApiError(error, context = '操作') {
  if (error.response) {
    const { status, data } = error.response
    
    switch (status) {
      case 400:
        return data.message || `${context}失败：请求参数错误`
      case 404:
        return `${context}失败：资源不存在`
      case 429:
        return `${context}失败：请求过于频繁，请稍后重试`
      case 500:
        return `${context}失败：服务器内部错误`
      default:
        return `${context}失败：${data.message || `服务器错误 (${status})`}`
    }
  } else if (error.request) {
    return `${context}失败：网络连接错误，请检查网络设置`
  } else {
    return `${context}失败：${error.message}`
  }
}
```

#### 验收条件
1. **接口功能验证**：
   - 所有换热器相关接口能正常调用
   - 参数验证和错误处理完善
   - 返回数据格式正确，能转换为模型对象

2. **数据模型验证**：
   - 数据模型类能正确初始化API数据
   - 模型方法能正确计算衍生属性
   - 类型转换（如日期）正确

3. **查询参数验证**：
   - 查询参数构建工具工作正常
   - 分页、排序、过滤参数正确传递
   - 时间范围参数格式正确

4. **错误处理验证**：
   - API错误能正确转换为用户友好消息
   - 网络错误能正确处理
   - 数据转换错误能妥善处理

#### 产出物清单
- ✓ src/api/heat-exchanger.js（换热器API接口）
- ✓ src/models/heat-exchanger.js（数据模型）
- ✓ src/utils/api-response.js（API响应处理工具）
- ✓ 完整的换热器数据接口集
- ✓ 数据模型转换功能
- ✓ 查询参数构建工具

---

### T2.1.3 实现实时数据SSE连接

#### 任务描述
1. **封装EventSource连接**：
   - 创建SSE连接管理类
   - 实现连接建立和维护
   - 配置请求头和认证

2. **实现事件处理机制**：
   - 定义实时数据事件类型
   - 实现事件监听和处理
   - 数据解析和转换

3. **实现连接管理功能**：
   - 连接状态管理
   - 错误重连机制（指数退避）
   - 连接生命周期管理

#### 技术细节与实现步骤

**步骤1：创建SSE连接管理类**
```javascript
// src/utils/sse-client.js
/**
 * Server-Sent Events (SSE) 客户端
 */

export class SSEClient {
  constructor(options = {}) {
    // 配置选项
    this.options = {
      url: '',
      heatExchangerId: null,
      withCredentials: false,
      headers: {},
      retry: {
        maxAttempts: 10,
        initialDelay: 1000,
        maxDelay: 30000,
        backoffFactor: 2
      },
      heartbeat: {
        interval: 30000, // 30秒心跳
        timeout: 10000   // 10秒超时
      },
      ...options
    }
    
    // 状态
    this.eventSource = null
    this.reconnectAttempts = 0
    this.reconnectTimer = null
    this.heartbeatTimer = null
    this.lastHeartbeat = null
    this.listeners = new Map()
    
    // 连接状态
    this.connectionState = {
      connected: false,
      connecting: false,
      lastError: null,
      lastConnectTime: null,
      lastMessageTime: null
    }
    
    // 绑定方法
    this.handleOpen = this.handleOpen.bind(this)
    this.handleMessage = this.handleMessage.bind(this)
    this.handleError = this.handleError.bind(this)
    this.handleClose = this.handleClose.bind(this)
  }
  
  /**
   * 建立连接
   */
  connect() {
    if (this.connectionState.connecting || this.connectionState.connected) {
      console.warn('SSE连接已建立或正在建立中')
      return
    }
    
    this.connectionState.connecting = true
    this.connectionState.lastError = null
    
    try {
      // 构建连接URL
      let url = this.options.url
      if (this.options.heatExchangerId) {
        const separator = url.includes('?') ? '&' : '?'
        url += `${separator}heat_exchanger_id=${this.options.heatExchangerId}`
      }
      
      // 创建EventSource实例
      this.eventSource = new EventSource(url, {
        withCredentials: this.options.withCredentials
      })
      
      // 添加事件监听
      this.eventSource.addEventListener('open', this.handleOpen)
      this.eventSource.addEventListener('message', this.handleMessage)
      this.eventSource.addEventListener('error', this.handleError)
      
      // 设置连接超时检查
      setTimeout(() => {
        if (this.connectionState.connecting && !this.connectionState.connected) {
          this.handleError(new Error('连接超时'))
        }
      }, 10000)
      
    } catch (error) {
      this.handleError(error)
    }
  }
  
  /**
   * 处理连接打开事件
   */
  handleOpen(event) {
    console.log('SSE连接已建立')
    
    this.connectionState.connecting = false
    this.connectionState.connected = true
    this.connectionState.lastConnectTime = new Date()
    this.reconnectAttempts = 0
    
    // 触发连接打开事件
    this.emit('connect', { event, timestamp: new Date() })
    
    // 开始心跳检测
    this.startHeartbeat()
    
    // 清理重连定时器
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer)
      this.reconnectTimer = null
    }
  }
  
  /**
   * 处理消息事件
   */
  handleMessage(event) {
    this.connectionState.lastMessageTime = new Date()
    
    try {
      const data = JSON.parse(event.data)
      const eventType = data.event_type || 'data_update'
      
      // 更新最后心跳时间
      if (eventType === 'heartbeat') {
        this.lastHeartbeat = new Date()
        this.emit('heartbeat', { event, data, timestamp: new Date() })
        return
      }
      
      // 处理数据更新事件
      this.emit(eventType, { event, data, timestamp: new Date() })
      
    } catch (error) {
      console.error('SSE消息解析失败:', error, event.data)
      this.emit('parse_error', { error, rawData: event.data })
    }
  }
  
  /**
   * 处理错误事件
   */
  handleError(error) {
    console.error('SSE连接错误:', error)
    
    this.connectionState.connecting = false
    this.connectionState.lastError = error.message || '未知错误'
    
    // 触发错误事件
    this.emit('error', { error, timestamp: new Date() })
    
    // 关闭当前连接
    this.disconnect()
    
    // 尝试重连
    if (this.reconnectAttempts < this.options.retry.maxAttempts) {
      this.scheduleReconnect()
    } else {
      console.error('已达到最大重连次数，停止重连')
      this.emit('max_reconnect', { attempts: this.reconnectAttempts })
    }
  }
  
  /**
   * 处理连接关闭
   */
  handleClose() {
    this.connectionState.connected = false
    
    // 触发连接关闭事件
    this.emit('disconnect', { timestamp: new Date() })
    
    // 停止心跳检测
    this.stopHeartbeat()
  }
  
  /**
   * 安排重连
   */
  scheduleReconnect() {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer)
    }
    
    this.reconnectAttempts++
    
    // 计算重连延迟（指数退避）
    const delay = Math.min(
      this.options.retry.initialDelay * Math.pow(this.options.retry.backoffFactor, this.reconnectAttempts - 1),
      this.options.retry.maxDelay
    )
    
    console.log(`将在 ${delay}ms 后重连 (尝试 ${this.reconnectAttempts}/${this.options.retry.maxAttempts})`)
    
    this.reconnectTimer = setTimeout(() => {
      this.emit('reconnecting', { attempt: this.reconnectAttempts, delay })
      this.connect()
    }, delay)
  }
  
  /**
   * 开始心跳检测
   */
  startHeartbeat() {
    if (this.heartbeatTimer) {
      clearInterval(this.heartbeatTimer)
    }
    
    this.lastHeartbeat = new Date()
    
    this.heartbeatTimer = setInterval(() => {
      const now = new Date()
      const timeSinceLastHeartbeat = now - this.lastHeartbeat
      
      if (timeSinceLastHeartbeat > this.options.heartbeat.timeout) {
        console.warn('心跳检测超时，尝试重连')
        this.handleError(new Error('心跳超时'))
      }
    }, this.options.heartbeat.interval)
  }
  
  /**
   * 停止心跳检测
   */
  stopHeartbeat() {
    if (this.heartbeatTimer) {
      clearInterval(this.heartbeatTimer)
      this.heartbeatTimer = null
    }
  }
  
  /**
   * 断开连接
   */
  disconnect() {
    if (this.eventSource) {
      this.eventSource.close()
      this.eventSource = null
    }
    
    this.handleClose()
    
    // 清理定时器
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer)
      this.reconnectTimer = null
    }
    
    this.stopHeartbeat()
    
    this.connectionState.connected = false
    this.connectionState.connecting = false
  }
  
  /**
   * 添加事件监听
   */
  on(event, callback) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, new Set())
    }
    this.listeners.get(event).add(callback)
    
    // 返回取消监听函数
    return () => {
      this.off(event, callback)
    }
  }
  
  /**
   * 移除事件监听
   */
  off(event, callback) {
    if (this.listeners.has(event)) {
      this.listeners.get(event).delete(callback)
    }
  }
  
  /**
   * 触发事件
   */
  emit(event, data) {
    if (this.listeners.has(event)) {
      this.listeners.get(event).forEach(callback => {
        try {
          callback(data)
        } catch (error) {
          console.error(`SSE事件监听器执行失败 (${event}):`, error)
        }
      })
    }
  }
  
  /**
   * 获取连接状态
   */
  getConnectionState() {
    return {
      ...this.connectionState,
      reconnectAttempts: this.reconnectAttempts,
      isOnline: this.connectionState.connected
    }
  }
}
```

**步骤2：创建实时数据API模块**
```javascript
// src/api/realtime.js
import { SSEClient } from '@/utils/sse-client'

/**
 * 实时数据API接口
 */

// 全局SSE客户端实例映射
const sseClients = new Map()

/**
 * 创建或获取SSE客户端实例
 * @param {string|number} heatExchangerId - 换热器ID
 * @param {Object} options - 连接选项
 * @returns {SSEClient} SSE客户端实例
 */
export function getRealtimeClient(heatExchangerId, options = {}) {
  const clientId = String(heatExchangerId)
  
  // 如果已存在客户端，先断开
  if (sseClients.has(clientId)) {
    const existingClient = sseClients.get(clientId)
    if (existingClient.getConnectionState().connected) {
      console.log(`已存在 ${heatExchangerId} 的连接，先断开`)
      existingClient.disconnect()
    }
  }
  
  // 创建新的客户端
  const baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
  const url = `${baseUrl}/api/realtime-stream`
  
  const client = new SSEClient({
    url,
    heatExchangerId,
    headers: {
      'Accept': 'text/event-stream'
    },
    ...options
  })
  
  // 存储客户端
  sseClients.set(clientId, client)
  
  return client
}

/**
 * 断开指定换热器的SSE连接
 * @param {string|number} heatExchangerId - 换热器ID
 */
export function disconnectRealtimeClient(heatExchangerId) {
  const clientId = String(heatExchangerId)
  
  if (sseClients.has(clientId)) {
    const client = sseClients.get(clientId)
    client.disconnect()
    sseClients.delete(clientId)
  }
}

/**
 * 断开所有SSE连接
 */
export function disconnectAllRealtimeClients() {
  sseClients.forEach((client, heatExchangerId) => {
    client.disconnect()
  })
  sseClients.clear()
}

/**
 * 获取所有SSE客户端状态
 * @returns {Array} 客户端状态列表
 */
export function getAllRealtimeClientsStatus() {
  const statusList = []
  
  sseClients.forEach((client, heatExchangerId) => {
    statusList.push({
      heatExchangerId,
      ...client.getConnectionState()
    })
  })
  
  return statusList
}

/**
 * 实时数据API对象
 */
export const realtimeAPI = {
  // 连接管理
  connect: getRealtimeClient,
  disconnect: disconnectRealtimeClient,
  disconnectAll: disconnectAllRealtimeClients,
  getStatus: getAllRealtimeClientsStatus,
  
  /**
   * 创建带认证的SSE客户端
   * @param {string|number} heatExchangerId - 换热器ID
   * @param {string} token - 认证Token
   * @returns {SSEClient} SSE客户端实例
   */
  connectWithAuth(heatExchangerId, token) {
    // 注意：标准EventSource不支持自定义header，这里需要特殊处理
    // 通常SSE认证通过URL参数或Cookie实现
    
    const baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
    const url = `${baseUrl}/api/realtime-stream?heat_exchanger_id=${heatExchangerId}&token=${token}`
    
    const client = new SSEClient({
      url,
      heatExchangerId
    })
    
    const clientId = String(heatExchangerId)
    sseClients.set(clientId, client)
    
    return client
  }
}

export default realtimeAPI
```

**步骤3：创建实时数据处理工具**
```javascript
// src/utils/realtime-data-processor.js
/**
 * 实时数据处理工具
 */

/**
 * 实时数据处理类
 */
export class RealtimeDataProcessor {
  constructor(options = {}) {
    this.options = {
      bufferSize: 100, // 缓冲区大小
      updateInterval: 1000, // 更新间隔（毫秒）
      debounceTime: 500, // 防抖时间
      ...options
    }
    
    this.dataBuffer = new Map()
    this.updateCallbacks = new Set()
    this.lastUpdateTime = null
    this.updateTimer = null
    this.isProcessing = false
  }
  
  /**
   * 处理实时数据
   * @param {Object} data - 原始数据
   * @param {string} eventType - 事件类型
   */
  processData(data, eventType = 'data_update') {
    const { heat_exchanger_id: heatExchangerId, ...payload } = data
    
    if (!heatExchangerId) {
      console.warn('实时数据缺少heat_exchanger_id')
      return
    }
    
    // 根据事件类型处理数据
    switch (eventType) {
      case 'parameters_update':
        this.processParametersUpdate(heatExchangerId, payload)
        break
        
      case 'k_value_update':
        this.processKValueUpdate(heatExchangerId, payload)
        break
        
      case 'alert_new':
        this.processNewAlert(heatExchangerId, payload)
        break
        
      case 'health_status_update':
        this.processHealthStatusUpdate(heatExchangerId, payload)
        break
        
      default:
        console.warn(`未知的实时事件类型: ${eventType}`, data)
    }
  }
  
  /**
   * 处理参数更新
   */
  processParametersUpdate(heatExchangerId, data) {
    const key = `params_${heatExchangerId}`
    const now = new Date()
    
    // 添加时间戳
    const processedData = {
      ...data,
      timestamp: now,
      heatExchangerId
    }
    
    // 存储到缓冲区
    if (!this.dataBuffer.has(key)) {
      this.dataBuffer.set(key, [])
    }
    
    const buffer = this.dataBuffer.get(key)
    buffer.push(processedData)
    
    // 保持缓冲区大小
    if (buffer.length > this.options.bufferSize) {
      buffer.shift()
    }
    
    // 触发更新
    this.scheduleUpdate()
  }
  
  /**
   * 处理K值更新
   */
  processKValueUpdate(heatExchangerId, data) {
    const key = `kvalue_${heatExchangerId}`
    const now = new Date()
    
    const processedData = {
      ...data,
      timestamp: now,
      heatExchangerId
    }
    
    if (!this.dataBuffer.has(key)) {
      this.dataBuffer.set(key, [])
    }
    
    const buffer = this.dataBuffer.get(key)
    buffer.push(processedData)
    
    if (buffer.length > this.options.bufferSize) {
      buffer.shift()
    }
    
    this.scheduleUpdate()
  }
  
  /**
   * 处理新报警
   */
  processNewAlert(heatExchangerId, data) {
    const key = `alerts_${heatExchangerId}`
    
    if (!this.dataBuffer.has(key)) {
      this.dataBuffer.set(key, [])
    }
    
    const buffer = this.dataBuffer.get(key)
    buffer.unshift(data) // 新报警添加到前面
    
    if (buffer.length > 20) { // 最多保存20个报警
      buffer.pop()
    }
    
    // 立即触发报警更新（不防抖）
    this.triggerUpdate('alert', { heatExchangerId, alert: data })
  }
  
  /**
   * 处理健康状态更新
   */
  processHealthStatusUpdate(heatExchangerId, data) {
    const key = `health_${heatExchangerId}`
    
    this.dataBuffer.set(key, {
      ...data,
      timestamp: new Date(),
      heatExchangerId
    })
    
    this.scheduleUpdate()
  }
  
  /**
   * 安排更新（防抖）
   */
  scheduleUpdate() {
    if (this.updateTimer) {
      clearTimeout(this.updateTimer)
    }
    
    this.updateTimer = setTimeout(() => {
      this.processBufferedData()
    }, this.options.debounceTime)
  }
  
  /**
   * 处理缓冲数据
   */
  processBufferedData() {
    if (this.isProcessing) return
    
    this.isProcessing = true
    
    try {
      const now = new Date()
      const updateData = {}
      
      // 收集所有需要更新的数据
      this.dataBuffer.forEach((buffer, key) => {
        if (Array.isArray(buffer) && buffer.length > 0) {
          // 取最新数据
          updateData[key] = buffer[buffer.length - 1]
        } else if (buffer && typeof buffer === 'object') {
          updateData[key] = buffer
        }
      })
      
      // 触发更新回调
      if (Object.keys(updateData).length > 0) {
        this.triggerUpdate('data', updateData)
        this.lastUpdateTime = now
      }
      
    } catch (error) {
      console.error('处理实时数据失败:', error)
    } finally {
      this.isProcessing = false
    }
  }
  
  /**
   * 触发更新
   */
  triggerUpdate(type, data) {
    this.updateCallbacks.forEach(callback => {
      try {
        callback(type, data)
      } catch (error) {
        console.error('实时数据更新回调执行失败:', error)
      }
    })
  }
  
  /**
   * 注册更新回调
   */
  onUpdate(callback) {
    this.updateCallbacks.add(callback)
    
    // 返回取消注册函数
    return () => {
      this.updateCallbacks.delete(callback)
    }
  }
  
  /**
   * 获取缓冲数据
   */
  getBufferData(heatExchangerId, dataType = 'params') {
    const key = `${dataType}_${heatExchangerId}`
    return this.dataBuffer.get(key) || null
  }
  
  /**
   * 获取历史数据（从缓冲区）
   */
  getHistoryData(heatExchangerId, dataType = 'params', limit = 50) {
    const key = `${dataType}_${heatExchangerId}`
    const buffer = this.dataBuffer.get(key)
    
    if (!Array.isArray(buffer)) return []
    
    return buffer.slice(-limit)
  }
  
  /**
   * 清空缓冲区
   */
  clearBuffer(heatExchangerId = null, dataType = null) {
    if (heatExchangerId && dataType) {
      const key = `${dataType}_${heatExchangerId}`
      this.dataBuffer.delete(key)
    } else if (heatExchangerId) {
      // 清空该换热器的所有数据
      const prefix = `${heatExchangerId}_`
      this.dataBuffer.forEach((_, key) => {
        if (key.startsWith(prefix)) {
          this.dataBuffer.delete(key)
        }
      })
    } else {
      // 清空所有缓冲区
      this.dataBuffer.clear()
    }
  }
  
  /**
   * 销毁处理器
   */
  destroy() {
    if (this.updateTimer) {
      clearTimeout(this.updateTimer)
      this.updateTimer = null
    }
    
    this.dataBuffer.clear()
    this.updateCallbacks.clear()
    this.isProcessing = false
  }
}
```

#### 验收条件
1. **SSE连接验证**：
   - 能成功建立SSE连接
   - 连接状态能正确管理
   - 认证信息能正确传递

2. **事件处理验证**：
   - 能正确接收和处理推送数据
   - 不同事件类型能正确分发
   - 数据解析和转换正确

3. **连接管理验证**：
   - 断开后能自动重连（指数退避）
   - 心跳检测能正确工作
   - 多个连接能正确管理

4. **数据处理验证**：
   - 实时数据能正确缓冲和处理
   - 数据更新能正确通知组件
   - 防抖机制能防止频繁更新

#### 产出物清单
- ✓ src/utils/sse-client.js（SSE连接管理）
- ✓ src/api/realtime.js（实时数据API）
- ✓ src/utils/realtime-data-processor.js（实时数据处理）
- ✓ 完整的SSE连接管理功能
- ✓ 实时数据处理和缓冲机制
- ✓ 连接状态监控和错误恢复

---

## 模块完成标准

### 总体验收条件
1. **API服务层完整**：
   - HTTP请求工具工作正常，错误处理完善
   - 换热器相关API接口完整可用
   - 实时数据SSE连接稳定可靠

2. **错误处理完善**：
   - 网络错误、服务器错误能正确处理
   - Token过期能自动刷新
   - 用户友好的错误提示

3. **数据管理规范**：
   - API数据能正确转换为模型对象
   - 实时数据能正确缓冲和处理
   - 数据更新能正确通知组件

4. **性能优化到位**：
   - 请求防抖和重试机制完善
   - 实时数据更新频率控制合理
   - 内存管理良好，无内存泄漏

### 产出物总览
- ✓ 完整的HTTP请求工具层
- ✓ 完整的换热器API接口集
- ✓ 完整的实时数据SSE连接管理
- ✓ 数据模型和转换工具
- ✓ 错误处理和状态管理

### 下一模块准备
完成本模块后，项目已具备：
1. 完整的数据获取能力
2. 稳定的实时数据推送
3. 规范的错误处理机制
4. 可扩展的API服务架构

可以进入下一模块：工具函数模块开发