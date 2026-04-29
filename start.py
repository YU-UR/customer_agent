#!/usr/bin/env python3
"""
智能电商客服与销售支持系统启动脚本
"""
import os
import sys
import asyncio
import logging
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.core.config import settings

def check_environment():
    """检查环境配置"""
    required_vars = [
        'OPENAI_API_KEY',
        'MYSQL_HOST',
        'REDIS_HOST',
        'MILVUS_URL'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not getattr(settings, var, None):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ 缺少必要的环境变量: {', '.join(missing_vars)}")
        print("请检查 .env 文件配置")
        return False
    
    print("✅ 环境配置检查通过")
    return True

def create_directories():
    """创建必要的目录"""
    directories = [
        'logs',
        'data',
        'temp'
    ]
    
    for directory in directories:
        dir_path = project_root / directory
        dir_path.mkdir(exist_ok=True)
        print(f"📁 创建目录: {directory}")

async def check_services():
    """检查外部服务连接"""
    print("🔍 检查外部服务连接...")
    
    # 这里可以添加对MySQL、Redis、Milvus等服务的连接检查
    # 暂时跳过具体实现
    print("⚠️  外部服务连接检查已跳过（需要实现具体检查逻辑）")

def main():
    """主启动函数"""
    print("🚀 启动智能电商客服与销售支持系统")
    print("=" * 50)
    
    # 检查环境配置
    if not check_environment():
        sys.exit(1)
    
    # 创建必要目录
    create_directories()
    
    # 检查外部服务
    asyncio.run(check_services())
    
    print("=" * 50)
    print("✅ 系统检查完成，准备启动服务...")
    print(f"🌐 服务地址: http://{settings.HOST}:{settings.PORT}")
    print(f"📚 API文档: http://{settings.HOST}:{settings.PORT}/docs")
    print("=" * 50)
    
    # 启动FastAPI应用
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )

if __name__ == "__main__":
    main()