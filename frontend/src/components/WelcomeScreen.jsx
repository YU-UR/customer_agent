import React from 'react'
import './WelcomeScreen.css'

const WelcomeScreen = ({ onQuickAction }) => {
  const features = [
    {
      icon: '📦',
      title: '订单查询',
      description: '查询订单状态和物流信息',
      action: '我想查询订单'
    },
    {
      icon: '🛍️',
      title: '商品推荐',
      description: '获取个性化商品推荐',
      action: '推荐商品'
    },
    {
      icon: '🎁',
      title: '优惠活动',
      description: '查看最新优惠和促销',
      action: '有什么优惠活动'
    },
    {
      icon: '🔄',
      title: '售后服务',
      description: '退换货和投诉处理',
      action: '我要退货'
    }
  ]
  
  return (
    <div className="welcome-screen">
      <div className="welcome-content">
        <h1>👋 您好，欢迎使用智能客服系统</h1>
        <p>我是您的专属智能助手，可以帮助您处理以下问题：</p>
        
        <div className="feature-grid">
          {features.map((feature, index) => (
            <div
              key={index}
              className="feature-card"
              onClick={() => onQuickAction(feature.action)}
            >
              <div className="feature-icon">{feature.icon}</div>
              <div className="feature-title">{feature.title}</div>
              <div className="feature-description">{feature.description}</div>
            </div>
          ))}
        </div>
        
        <div className="welcome-footer">
          <p>💡 提示：您也可以直接在下方输入框输入问题</p>
        </div>
      </div>
    </div>
  )
}

export default WelcomeScreen

