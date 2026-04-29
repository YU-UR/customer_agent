import React, { useState, useRef, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import useChatStore from '../store/chatStore'
import { chatAPI } from '../services/api'
import ChatHeader from '../components/ChatHeader'
import MessageList from '../components/MessageList'
import QuickReplies from '../components/QuickReplies'
import ChatInput from '../components/ChatInput'
import WelcomeScreen from '../components/WelcomeScreen'
import './ChatPage.css'

const ChatPage = () => {
  const navigate = useNavigate()
  const {
    messages,
    isLoading,
    userId,
    sessionId,
    addMessage,
    setLoading,
    setCurrentAgent,
    clearMessages
  } = useChatStore()
  
  const [showWelcome, setShowWelcome] = useState(true)
  const messagesEndRef = useRef(null)
  
  // 自动滚动到底部
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }
  
  useEffect(() => {
    scrollToBottom()
  }, [messages, isLoading])
  
  // 发送消息
  const handleSendMessage = async (text) => {chatAPI
    if (!text.trim() || isLoading) return
    
    // 隐藏欢迎屏幕
    setShowWelcome(false)
    
    // 添加用户消息
    addMessage({
      type: 'user',
      content: text
    })
    
    // 设置加载状态
    setLoading(true)
    
    try {
      addMessage({ type: 'bot', content: '' })
      const handle = chatAPI.streamSSEPost(
        text,
        userId,
        sessionId,
        (tok) => {
          if (tok) {
            useChatStore.getState().appendToLastMessage(tok)
          }
        },
        (data) => {
          let chunk = ''
          if (typeof data.final_response === 'string') chunk = data.final_response
          else if (Array.isArray(data.messages)) chunk = data.messages.map(m => m.content || '').join('')
          else if (typeof data.data === 'string') chunk = data.data
          if (chunk) {
            useChatStore.getState().appendToLastMessage(chunk)
          }
          if (data.current_agent) setCurrentAgent(data.current_agent)
        },
        (err) => {
          useChatStore.getState().updateLastMessage({ type: 'bot', content: '抱歉，服务暂时不可用，请稍后再试。', isError: true })
          setLoading(false)
        },
        () => { setLoading(false) }
      )
      window._sseHandle = handle
    } catch (error) {
      addMessage({ type: 'bot', content: '抱歉，服务暂时不可用，请稍后再试。', agent: 'general_agent', isError: true })
      setLoading(false)
    }
  }
  
  // 清除对话
  const handleClearChat = () => {
    if (window.confirm('确定要清除所有对话记录吗？')) {
      clearMessages()
      setShowWelcome(true)
    }
  }
  
  // 快捷回复
  const quickReplyOptions = [
    { text: '查询订单状态', icon: '📦' },
    { text: '推荐手机', icon: '📱' },
    { text: '有什么优惠券', icon: '🎁' },
    { text: '申请退货', icon: '🔄' }
  ]
  
  return (
    <div className="chat-page">
      <ChatHeader 
        onClear={handleClearChat}
        onHistory={() => navigate('/history')}
        onSettings={() => navigate('/settings')}
        onAuth={() => navigate('/auth')}
      />
      
      <div className="chat-content">
        {showWelcome && messages.length === 0 ? (
          <WelcomeScreen onQuickAction={handleSendMessage} />
        ) : (
          <MessageList 
            messages={messages}
            isLoading={isLoading}
            messagesEndRef={messagesEndRef}
          />
        )}
      </div>
      
      {!showWelcome && messages.length > 0 && (
        <QuickReplies 
          options={quickReplyOptions}
          onSelect={handleSendMessage}
        />
      )}
      
      <ChatInput 
        onSend={handleSendMessage}
        disabled={isLoading}
      />
    </div>
  )
}

export default ChatPage
