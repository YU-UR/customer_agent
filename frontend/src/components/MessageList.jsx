import React from 'react'
import Message from './Message'
import TypingIndicator from './TypingIndicator'
import './MessageList.css'

const MessageList = ({ messages, isLoading, messagesEndRef }) => {
  return (
    <div className="message-list">
      {messages.map((message) => (
        <Message key={message.id} message={message} />
      ))}
      {isLoading && <TypingIndicator />}
      <div ref={messagesEndRef} />
    </div>
  )
}

export default MessageList

