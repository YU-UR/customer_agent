import React from 'react'
import './TypingIndicator.css'

const TypingIndicator = () => {
  return (
    <div className="message bot typing-message">
      <div className="message-avatar">🤖</div>
      <div className="message-content">
        <div className="typing-indicator">
          <span className="typing-dot"></span>
          <span className="typing-dot"></span>
          <span className="typing-dot"></span>
        </div>
      </div>
    </div>
  )
}

export default TypingIndicator

