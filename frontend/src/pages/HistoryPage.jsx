import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { memoryAPI } from '../services/api'
import useChatStore from '../store/chatStore'
import './HistoryPage.css'

const HistoryPage = () => {
  const navigate = useNavigate()
  const { userId } = useChatStore()
  const [memories, setMemories] = useState([])
  const [loading, setLoading] = useState(true)
  
  useEffect(() => {
    loadMemories()
  }, [])
  
  const loadMemories = async () => {
    try {
      const data = await memoryAPI.getUserMemory(userId)
      setMemories(data.memories || [])
    } catch (error) {
      console.error('加载记忆失败:', error)
    } finally {
      setLoading(false)
    }
  }
  
  const handleClearMemories = async () => {
    if (window.confirm('确定要清除所有记忆吗？')) {
      try {
        await memoryAPI.clearUserMemory(userId)
        setMemories([])
      } catch (error) {
        console.error('清除记忆失败:', error)
        alert('清除失败，请稍后再试')
      }
    }
  }
  
  return (
    <div className="history-page">
      <div className="history-header">
        <button onClick={() => navigate('/')} className="back-btn">
          ← 返回
        </button>
        <h1>对话历史</h1>
        <button onClick={handleClearMemories} className="clear-btn">
          清除记忆
        </button>
      </div>
      
      <div className="history-content">
        {loading ? (
          <div className="loading">加载中...</div>
        ) : memories.length === 0 ? (
          <div className="empty-state">
            <p>📝</p>
            <p>暂无历史记忆</p>
          </div>
        ) : (
          <div className="memory-list">
            {memories.map((memory, index) => (
              <div key={index} className="memory-item">
                <div className="memory-content">{memory.memory || memory.content}</div>
                <div className="memory-meta">
                  {memory.created_at && (
                    <span className="memory-time">
                      {new Date(memory.created_at).toLocaleString('zh-CN')}
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

export default HistoryPage

