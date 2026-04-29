import React, { useState, useRef } from 'react'
import './ChatInput.css'

const ChatInput = ({ onSend, disabled }) => {
  const [message, setMessage] = useState('')
  const inputRef = useRef(null)
  
  const handleSubmit = (e) => {
    e.preventDefault()
    if (message.trim() && !disabled) {
      onSend(message.trim())
      setMessage('')
      inputRef.current?.focus()
    }
  }
  
  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit(e)
    }
  }
  
  return (
    <div className="chat-input-area">
      <form onSubmit={handleSubmit} className="input-wrapper">
        <div className="input-actions">
          <button 
            type="button" 
            className="attachment-btn" 
            title="上传图片"
            disabled={disabled}
          >
            📎
          </button>
          <button 
            type="button" 
            className="attachment-btn" 
            title="表情"
            disabled={disabled}
          >
            😊
          </button>
        </div>
        
        <input
          ref={inputRef}
          type="text"
          className="message-input"
          placeholder="输入您的问题..."
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyPress={handleKeyPress}
          disabled={disabled}
        />
        
        <button 
          type="submit" 
          className="send-btn"
          disabled={disabled || !message.trim()}
        >
          ➤
        </button>
      </form>
    </div>
  )
}

export default ChatInput

