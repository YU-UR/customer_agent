# 智能电商客服系统 - 前端

基于 React + Vite 构建的现代化智能客服前端应用。

## ✨ 功能特性

- 🤖 **智能对话** - 实时对话交互，支持多智能体路由
- 💬 **消息管理** - 消息历史记录，支持查看和清除
- 🎯 **快捷回复** - 预设常用问题，一键发送
- 🎨 **现代UI** - 渐变配色，流畅动画
- 📱 **响应式设计** - 完美适配桌面端和移动端
- 🔄 **打字动画** - 真实的打字指示器效果
- 🏷️ **智能体标识** - 清晰显示当前处理的专家类型
- ⚙️ **系统设置** - 查看系统信息和工具状态

## 🚀 快速开始

### 1. 安装依赖

```bash
cd frontend
npm install
```

### 2. 配置环境变量

复制 `.env.example` 为 `.env` 并配置：

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```env
VITE_API_URL=http://localhost:8001
VITE_API_KEY=你的API密钥
```

### 3. 启动开发服务器

```bash
npm run dev
```

应用将在 `http://localhost:3000` 启动

### 4. 构建生产版本

```bash
npm run build
```

构建产物将输出到 `dist` 目录

### 5. 预览生产版本

```bash
npm run preview
```

## 📁 项目结构

```
frontend/
├── src/
│   ├── components/          # 组件
│   │   ├── ChatHeader.jsx   # 聊天头部
│   │   ├── MessageList.jsx  # 消息列表
│   │   ├── Message.jsx      # 单条消息
│   │   ├── TypingIndicator.jsx  # 打字动画
│   │   ├── QuickReplies.jsx # 快捷回复
│   │   ├── ChatInput.jsx    # 输入框
│   │   └── WelcomeScreen.jsx # 欢迎屏幕
│   ├── pages/               # 页面
│   │   ├── ChatPage.jsx     # 聊天页面
│   │   ├── HistoryPage.jsx  # 历史页面
│   │   └── SettingsPage.jsx # 设置页面
│   ├── services/            # 服务
│   │   └── api.js           # API接口
│   ├── store/               # 状态管理
│   │   └── chatStore.js     # 聊天状态
│   ├── App.jsx              # 主应用
│   ├── main.jsx             # 入口文件
│   └── index.css            # 全局样式
├── index.html               # HTML模板
├── vite.config.js           # Vite配置
├── package.json             # 依赖配置
└── README.md                # 说明文档
```

## 🎨 技术栈

- **React 18** - UI框架
- **Vite** - 构建工具
- **React Router** - 路由管理
- **Zustand** - 状态管理
- **Axios** - HTTP客户端
- **Lucide React** - 图标库（可选）

## 📱 页面说明

### 1. 聊天页面 (/)
- 主要的对话界面
- 支持实时消息发送和接收
- 显示智能体类型标识
- 快捷回复按钮

### 2. 历史页面 (/history)
- 查看用户的对话历史和记忆
- 支持清除所有记忆
- 显示记忆时间戳

### 3. 设置页面 (/settings)
- 显示用户ID和会话ID
- 查看系统信息和版本
- MCP工具健康状态
- 支持重新生成会话

## 🔌 API集成

### 环境配置

在 `.env` 文件中配置：

```env
VITE_API_URL=http://localhost:8001  # 后端API地址
VITE_API_KEY=your_api_key_here      # API密钥
```

### API接口

- `POST /api/v1/chat` - 发送消息
- `POST /api/v1/chat/stream` - 流式发送消息
- `GET /api/v1/memory/:userId` - 获取用户记忆
- `DELETE /api/v1/memory/:userId` - 清除用户记忆
- `GET /api/v1/tools` - 获取可用工具
- `GET /api/v1/system/info` - 获取系统信息

## 🎯 智能体类型

系统支持以下智能体类型，会在消息中显示对应标识：

- 📦 订单专家 (order_agent)
- 🛍️ 商品顾问 (product_agent)
- 🎁 优惠专员 (promotion_agent)
- 🔧 售后专家 (after_sales_agent)
- 💬 客服助手 (general_agent)

## 🛠️ 开发指南

### 添加新组件

1. 在 `src/components/` 创建组件文件
2. 创建对应的CSS文件
3. 在需要的地方导入使用

### 添加新页面

1. 在 `src/pages/` 创建页面文件
2. 在 `App.jsx` 中添加路由
3. 创建对应的CSS文件

### 状态管理

使用 Zustand 进行状态管理，参考 `src/store/chatStore.js`

```javascript
import useChatStore from '../store/chatStore'

const { messages, addMessage } = useChatStore()
```

## 📝 注意事项

1. **API密钥安全**：不要将真实的API密钥提交到代码仓库
2. **CORS配置**：确保后端API已正确配置CORS
3. **代理配置**：开发环境使用Vite代理避免CORS问题
4. **错误处理**：所有API调用都包含错误处理
5. **响应式设计**：确保在各种设备上测试

## 🚀 部署

### 使用Nginx部署

1. 构建项目：
```bash
npm run build
```

2. 将 `dist` 目录内容复制到Nginx web目录

3. 配置Nginx：
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        root /path/to/dist;
        try_files $uri $uri/ /index.html;
    }
    
    location /api {
        proxy_pass http://localhost:8001;
    }
}
```

### 使用Docker部署

创建 `Dockerfile`：
```dockerfile
FROM node:18-alpine as build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

构建和运行：
```bash
docker build -t customer-service-frontend .
docker run -d -p 80:80 customer-service-frontend
```

## 📄 许可证

MIT License


