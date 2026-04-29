"""
自动创建数据库表
"""
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from app.db.base import Base, engine
from app.db.models import (
    User,
    Conversation,
    Message,
    MessageFeedback,
    AgentOutput,
    AgentPerformance,
    AgentUsageStats,
    SystemMetrics,
    KnowledgeBase,
    ErrorLog
)


def create_all_tables():
    """创建所有数据库表"""
    print("开始创建数据库表...")
    
    try:
        # 创建所有表
        Base.metadata.create_all(bind=engine)
        
        print("✅ 数据库表创建成功！")
        print("\n创建的表包括:")
        print("  1. users - 用户表")
        print("  2. conversations - 会话表")
        print("  3. messages - 消息记录表")
        print("  4. message_feedbacks - 消息反馈表")
        print("  5. agent_outputs - 智能体输出记录表")
        print("  6. agent_performance - 智能体性能表")
        print("  7. agent_usage_stats - 智能体使用统计表")
        print("  8. system_metrics - 系统指标表")
        print("  9. knowledge_base - 知识库表")
        print(" 10. error_logs - 错误日志表")
        
    except Exception as e:
        print(f"❌ 创建数据库表失败: {e}")
        raise


def drop_all_tables():
    """删除所有数据库表（慎用！）"""
    print("⚠️  警告：即将删除所有数据库表！")
    confirm = input("确认删除所有表？(yes/no): ")
    
    if confirm.lower() == 'yes':
        try:
            Base.metadata.drop_all(bind=engine)
            print("✅ 所有表已删除")
        except Exception as e:
            print(f"❌ 删除表失败: {e}")
            raise
    else:
        print("操作已取消")


def recreate_all_tables():
    """重新创建所有表（先删除后创建）"""
    print("⚠️  警告：即将删除并重新创建所有数据库表！")
    confirm = input("确认重新创建所有表？(yes/no): ")
    
    if confirm.lower() == 'yes':
        try:
            # 删除所有表
            Base.metadata.drop_all(bind=engine)
            print("✅ 旧表已删除")
            
            # 创建所有表
            Base.metadata.create_all(bind=engine)
            print("✅ 新表已创建")
            
        except Exception as e:
            print(f"❌ 重新创建表失败: {e}")
            raise
    else:
        print("操作已取消")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='数据库表管理工具')
    parser.add_argument(
        'action',
        choices=['create', 'drop', 'recreate'],
        help='操作类型: create(创建), drop(删除), recreate(重新创建)'
    )
    
    args = parser.parse_args()
    
    if args.action == 'create':
        create_all_tables()
    elif args.action == 'drop':
        drop_all_tables()
    elif args.action == 'recreate':
        recreate_all_tables()
