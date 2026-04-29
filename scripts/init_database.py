#!/usr/bin/env python3
"""
数据库初始化脚本
"""
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import asyncio
from app.db.auto_create_tables import create_all_tables, recreate_all_tables
from app.db.session import test_db_connection
from app.core.config import settings
from app.utils.log_utils import logger_util

logger = logger_util.get_logger(__name__)


def main():
    """主函数"""
    print("=" * 60)
    print("智能电商客服系统 - 数据库初始化工具")
    print("=" * 60)
    print()
    
    # 1. 显示配置信息
    print("📋 当前配置:")
    print(f"  数据库类型: MySQL")
    print(f"  主机地址: {settings.MYSQL_HOST}")
    print(f"  端口: {settings.MYSQL_PORT}")
    print(f"  数据库名: {settings.MYSQL_DATABASE}")
    print(f"  用户名: {settings.MYSQL_USER}")
    print()
    
    # 2. 测试数据库连接
    print("🔍 测试数据库连接...")
    if not test_db_connection():
        print("❌ 数据库连接失败！请检查配置和数据库服务状态。")
        return
    print("✅ 数据库连接成功！")
    print()
    
    # 3. 询问用户操作
    print("请选择操作:")
    print("  1. 创建所有表（如果表已存在则跳过）")
    print("  2. 重新创建所有表（会删除现有数据！）")
    print("  3. 退出")
    print()
    
    choice = input("请输入选项 (1-3): ").strip()
    
    if choice == "1":
        print()
        print("⚙️  开始创建数据库表...")
        create_all_tables()
        print()
        print("=" * 60)
        print("✅ 数据库初始化完成！")
        print("=" * 60)
        
    elif choice == "2":
        print()
        print("⚠️  警告：此操作将删除所有现有数据！")
        confirm = input("确认重新创建所有表？(yes/no): ").strip().lower()
        
        if confirm == "yes":
            print()
            print("⚙️  开始重新创建数据库表...")
            recreate_all_tables()
            print()
            print("=" * 60)
            print("✅ 数据库重新创建完成！")
            print("=" * 60)
        else:
            print("操作已取消")
            
    elif choice == "3":
        print("退出程序")
    else:
        print("无效的选项")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n操作已取消")
    except Exception as e:
        logger.error(f"数据库初始化失败: {e}", exc_info=True)
        print(f"\n❌ 错误: {e}")
        sys.exit(1)

