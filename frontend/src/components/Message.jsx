import React from 'react'
import './Message.css'

const AGENT_ICONS = {
  'order_agent': '📦',
  'product_agent': '🛍️',
  'promotion_agent': '🎁',
  'after_sales_agent': '🔧',
  'general_agent': '💬'
}

const AGENT_NAMES = {
  'order_agent': '订单专家',
  'product_agent': '商品顾问',
  'promotion_agent': '优惠专员',
  'after_sales_agent': '售后专家',
  'general_agent': '客服助手'
}

const Message = ({ message }) => {
  const { type, content, agent, timestamp, isError } = message
  
  const formatTime = (timestamp) => {
    if (!timestamp) return ''
    const date = new Date(timestamp)
    return date.toLocaleTimeString('zh-CN', { 
      hour: '2-digit', 
      minute: '2-digit' 
    })
  }
  
  return (
    <div className={`message ${type} ${isError ? 'error' : ''}`}>
      <div className="message-avatar">
        {type === 'user' ? '👤' : '🤖'}
      </div>
      
      <div className="message-content">
        {type === 'bot' && agent && (
          <div className="agent-badge">
            {AGENT_ICONS[agent] || '💬'} {AGENT_NAMES[agent] || '智能助手'}
          </div>
        )}
        
        <div className="message-bubble">
          {content}
        </div>
        
        <div className="message-time">
          {formatTime(timestamp)}
        </div>
      </div>
    </div>
  )
}

export default Message

