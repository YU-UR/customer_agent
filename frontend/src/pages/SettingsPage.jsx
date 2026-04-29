import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { systemAPI, toolsAPI, authAPI } from '../services/api'
import useChatStore from '../store/chatStore'
import './SettingsPage.css'

const SettingsPage = () => {
  const navigate = useNavigate()
  const { userId, sessionId, regenerateSession, setUserId } = useChatStore()
  const [systemInfo, setSystemInfo] = useState(null)
  const [toolsHealth, setToolsHealth] = useState(null)
  const [loading, setLoading] = useState(true)
  
  useEffect(() => {
    loadSystemInfo()
  }, [])
  
  const loadSystemInfo = async () => {
    try {
      const [info, health] = await Promise.all([
        systemAPI.getSystemInfo(),
        toolsAPI.checkHealth()
      ])
      setSystemInfo(info)
      setToolsHealth(health)
    } catch (error) {
      console.error('加载系统信息失败:', error)
    } finally {
      setLoading(false)
    }
  }
  
  const handleRegenerateSession = () => {
    if (window.confirm('确定要重新生成会话ID吗？')) {
      regenerateSession()
      alert('会话ID已重新生成')
    }
  }

  const handleLogout = async () => {
    if (window.confirm('确定要退出登录吗？')) {
      await authAPI.logout()
      setUserId(`user_${Math.random().toString(36).substr(2, 9)}`)
      alert('已退出登录')
    }
  }
  
  return (
    <div className="settings-page">
      <div className="settings-header">
        <button onClick={() => navigate('/')} className="back-btn">
          ← 返回
        </button>
        <h1>系统设置</h1>
        <div></div>
      </div>
      
      <div className="settings-content">
        {loading ? (
          <div className="loading">加载中...</div>
        ) : (
          <>
            {/* 用户信息 */}
            <section className="settings-section">
              <h2>👤 用户信息</h2>
              <div className="info-grid">
                <div className="info-item">
                  <span className="info-label">用户ID:</span>
                  <span className="info-value">{userId}</span>
                </div>
                <div className="info-item">
                  <span className="info-label">会话ID:</span>
                  <span className="info-value">{sessionId}</span>
                </div>
                <button onClick={handleRegenerateSession} className="action-btn">
                  重新生成会话
                </button>
                <button onClick={handleLogout} className="action-btn">
                  退出登录
                </button>
              </div>
            </section>
            
            {/* 系统信息 */}
            {systemInfo && (
              <section className="settings-section">
                <h2>⚙️ 系统信息</h2>
                <div className="info-grid">
                  <div className="info-item">
                    <span className="info-label">应用名称:</span>
                    <span className="info-value">{systemInfo.app_name}</span>
                  </div>
                  <div className="info-item">
                    <span className="info-label">版本:</span>
                    <span className="info-value">{systemInfo.version}</span>
                  </div>
                  <div className="info-item">
                    <span className="info-label">环境:</span>
                    <span className="info-value">{systemInfo.environment}</span>
                  </div>
                  <div className="info-item">
                    <span className="info-label">调试模式:</span>
                    <span className="info-value">
                      {systemInfo.debug ? '开启' : '关闭'}
                    </span>
                  </div>
                </div>
              </section>
            )}
            
            {/* MCP工具状态 */}
            {toolsHealth && (
              <section className="settings-section">
                <h2>🛠️ MCP工具状态</h2>
                <div className="health-status">
                  <div className={`status-badge ${toolsHealth.data?.status || 'unknown'}`}>
                    {toolsHealth.data?.status === 'healthy' ? '✅ 健康' : '❌ 异常'}
                  </div>
                  {toolsHealth.data?.tools_count && (
                    <p>已加载工具数: {toolsHealth.data.tools_count}</p>
                  )}
                  {toolsHealth.data?.categories && (
                    <div className="categories">
                      <p>工具分类:</p>
                      <div className="category-tags">
                        {toolsHealth.data.categories.map(cat => (
                          <span key={cat} className="category-tag">{cat}</span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </section>
            )}
            
            {/* 关于 */}
            <section className="settings-section">
              <h2>ℹ️ 关于</h2>
              <p className="about-text">
                智能电商客服与销售支持系统基于多智能体架构，
                集成了先进的AI技术、向量检索、长期记忆管理等功能，
                为用户提供7×24小时智能客户服务。
              </p>
            </section>
          </>
        )}
      </div>
    </div>
  )
}

export default SettingsPage
