import React from 'react'
import './QuickReplies.css'

const QuickReplies = ({ options, onSelect }) => {
  return (
    <div className="quick-replies">
      {options.map((option, index) => (
        <button
          key={index}
          className="quick-reply-btn"
          onClick={() => onSelect(option.text)}
        >
          {option.icon && <span className="btn-icon">{option.icon}</span>}
          {option.text}
        </button>
      ))}
    </div>
  )
}

export default QuickReplies

