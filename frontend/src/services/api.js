import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8001'
const API_KEY = import.meta.env.VITE_API_KEY || 'sk-760e83a1a8fa45ef8eeb8f946ce8e144'

const getToken = () => {
  try {
    const t1 = localStorage.getItem('auth_token')
    if (t1) return t1
    const t2 = sessionStorage.getItem('auth_token')
    return t2 || ''
  } catch (_) {
    return ''
  }
}

// 创建axios实例
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${getToken() || API_KEY}`
  },
  timeout: 30000
})

// 请求拦截器
apiClient.interceptors.request.use(
  (config) => {
    const token = getToken()
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`
    } else {
      config.headers['Authorization'] = `Bearer ${API_KEY}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
apiClient.interceptors.response.use(
  (response) => {
    return response.data
  },
  (error) => {
    console.error('API Error:', error)
    
    if (error.response) {
      // 服务器返回错误
      const message = error.response.data?.message || '服务器错误'
      throw new Error(message)
    } else if (error.request) {
      // 请求发出但没有收到响应
      throw new Error('网络错误，请检查连接')
    } else {
      // 其他错误
      throw new Error('请求失败')
    }
  }
)

// API方法
export const chatAPI = {
  // 发送消息
  sendMessage: async (message, userId, sessionId) => {
    return await apiClient.post('/api/v1/chat', {
      message,
      user_id: userId,
      session_id: sessionId
    })
  },
  
  streamSSEPost: (message, userId, sessionId, onToken, onChunk, onError, onEnd) => {
    const controller = new AbortController()
    const token = getToken()
    fetch(`${API_BASE_URL}/api/v1/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'text/event-stream',
        'Authorization': `Bearer ${token || API_KEY}`
      },
      body: JSON.stringify({ message, user_id: userId, session_id: sessionId }),
      signal: controller.signal
    }).then((res) => {
      const reader = res.body.getReader()
      const decoder = new TextDecoder('utf-8')
      let buffer = ''
      const pump = () => reader.read().then(({ done, value }) => {
        if (done) { if (onEnd) onEnd(); return }
        buffer += decoder.decode(value, { stream: true })
        const parts = buffer.split('\n\n')
        buffer = parts.pop()
        for (const part of parts) {
          const lines = part.split('\n')
          let eventName = null
          let dataStr = ''
          for (const line of lines) {
            if (line.startsWith('event:')) eventName = line.slice(6).trim()
            else if (line.startsWith('data:')) dataStr += line.slice(5).trim()
          }
          if (eventName === 'token') {
            try { const data = JSON.parse(dataStr); if (onToken) onToken(data.text || '') } catch (e) { onError && onError(e) }
          } else if (eventName === 'chunk') {
            try { const data = JSON.parse(dataStr); onChunk && onChunk(data) } catch (e) { onError && onError(e) }
          } else if (eventName === 'error') {
            onError && onError(dataStr)
          } else if (eventName === 'end') {
            try { const data = JSON.parse(dataStr); onEnd && onEnd(data) } catch (e) { onEnd && onEnd() }
          }
        }
        pump()
      })
      pump()
    }).catch((err) => { onError && onError(err) })
    return { abort: () => controller.abort() }
  }
}

export const memoryAPI = {
  // 获取用户记忆
  getUserMemory: async (userId) => {
    return await apiClient.get(`/api/v1/memory/${userId}`)
  },
  
  // 清除用户记忆
  clearUserMemory: async (userId) => {
    return await apiClient.delete(`/api/v1/memory/${userId}`)
  }
}

export const toolsAPI = {
  // 获取可用工具
  getTools: async (category = null) => {
    const params = category ? { category } : {}
    return await apiClient.get('/api/v1/tools', { params })
  },
  
  // 获取工具分类
  getCategories: async () => {
    return await apiClient.get('/api/v1/tools/categories')
  },
  
  // 调用工具
  callTool: async (toolName, params) => {
    return await apiClient.post(`/api/v1/tools/${toolName}/call`, params)
  },
  
  // 检查工具健康状态
  checkHealth: async () => {
    return await apiClient.get('/api/v1/tools/health')
  }
}

export const systemAPI = {
  // 健康检查
  healthCheck: async () => {
    return await apiClient.get('/health')
  },
  
  // 获取系统信息
  getSystemInfo: async () => {
    return await apiClient.get('/api/v1/system/info')
  }
}

export const authAPI = {
  login: async (payload) => {
    const res = await apiClient.post('/api/v1/auth/login', payload)
    return res
  },
  register: async (payload) => {
    const res = await apiClient.post('/api/v1/auth/register', payload)
    return res
  },
  logout: async () => {
    localStorage.removeItem('auth_token')
    localStorage.removeItem('auth_user')
    sessionStorage.removeItem('auth_token')
    sessionStorage.removeItem('auth_user')
    return { success: true }
  }
}

export default apiClient
