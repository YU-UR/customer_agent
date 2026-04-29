import React, { useMemo } from 'react'
import './ChatHeader.css'

const ChatHeader = ({ onClear, onHistory, onSettings, onAuth }) => {
  const isLoggedIn = useMemo(() => {
    try {
      return !!(localStorage.getItem('auth_token') || sessionStorage.getItem('auth_token'))
    } catch (_) { return false }
  }, [])
  return (
    <div className="chat-header">
      <div className="header-left">
        <div className="avatar">🤖</div>
        <div className="header-info">
          <h2>智能客服助手</h2>
          <div className="status">
            <span className="status-dot"></span>
            <span>在线服务中</span>
          </div>
        </div>
      </div>
      <div className="header-actions">
        <button onClick={onHistory} className="icon-btn" title="对话历史">
          📜
        </button>
        <button onClick={onClear} className="icon-btn" title="清除对话">
          🗑️
        </button>
        <button onClick={onSettings} className="icon-btn" title="设置">
          ⚙️
        </button>
        <button onClick={onAuth} className="icon-btn" title={isLoggedIn ? '已登录' : '登录/注册'}>
          {isLoggedIn ? '✅' : '🔐'}
        </button>
      </div>
    </div>
  )
}

export default ChatHeader
