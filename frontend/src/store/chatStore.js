import { create } from 'zustand'

const initialAuthUser = (() => {
  try {
    const raw = localStorage.getItem('auth_user')
    return raw ? JSON.parse(raw) : null
  } catch (_) {
    return null
  }
})()

const useChatStore = create((set, get) => ({
  // 状态
  messages: [],
  isLoading: false,
  currentAgent: null,
  userId: initialAuthUser?.user_id || `user_${Math.random().toString(36).substr(2, 9)}`,
  sessionId: `session_${Math.random().toString(36).substr(2, 9)}`,
  
  // 添加消息
  addMessage: (message) => {
    set((state) => ({
      messages: [...state.messages, {
        ...message,
        id: Date.now() + Math.random(),
        timestamp: new Date().toISOString()
      }]
    }))
  },
  
  // 设置加载状态
  setLoading: (isLoading) => set({ isLoading }),
  
  // 设置当前智能体
  setCurrentAgent: (agent) => set({ currentAgent: agent }),

  // 设置用户ID
  setUserId: (uid) => set({ userId: uid }),
  
  // 清除消息
  clearMessages: () => set({ messages: [] }),
  
  // 重新生成会话ID
  regenerateSession: () => set({
    sessionId: `session_${Math.random().toString(36).substr(2, 9)}`
  }),

  appendToLastMessage: (text) => {
    set((state) => {
      const msgs = [...state.messages]
      if (msgs.length === 0) return { messages: msgs }
      const last = msgs[msgs.length - 1]
      msgs[msgs.length - 1] = { ...last, content: (last.content || '') + text }
      return { messages: msgs }
    })
  },

  updateLastMessage: (patch) => {
    set((state) => {
      const msgs = [...state.messages]
      if (msgs.length === 0) return { messages: msgs }
      const last = msgs[msgs.length - 1]
      msgs[msgs.length - 1] = { ...last, ...patch }
      return { messages: msgs }
    })
  }
}))

export default useChatStore
