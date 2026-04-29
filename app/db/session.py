from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
from typing import Generator
from sqlalchemy.exc import SQLAlchemyError, OperationalError, IntegrityError, DataError

from app.core.config import settings
from app.core.exceptions import DatabaseError, ConfigurationError
from app.utils.log_utils import logger_util

logger = logger_util.get_logger(__name__)

# 创建数据库引擎
engine = create_engine(
    settings.mysql_url,
    pool_pre_ping=True,
    pool_recycle=3600,
    pool_size=5,
    max_overflow=10,
    echo=False
)

# 创建会话工厂
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False
)


@contextmanager
def get_db() -> Generator[Session, None, None]:
    """数据库会话上下文管理器"""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except OperationalError as e:
        session.rollback()
        logger.error(f"Database operational error: {str(e)}", exc_info=True)
        raise DatabaseError(
            message="数据库连接或操作失败",
            operation="database_operation",
            details={"original_error": str(e)}
        )
    except IntegrityError as e:
        session.rollback()
        logger.error(f"Database integrity error: {str(e)}", exc_info=True)
        raise DatabaseError(
            message="数据完整性约束违反",
            operation="database_integrity",
            details={"original_error": str(e)}
        )
    except DataError as e:
        session.rollback()
        logger.error(f"Database data error: {str(e)}", exc_info=True)
        raise DatabaseError(
            message="数据格式或类型错误",
            operation="database_data",
            details={"original_error": str(e)}
        )
    except SQLAlchemyError as e:
        session.rollback()
        logger.error(f"SQLAlchemy error: {str(e)}", exc_info=True)
        raise DatabaseError(
            message="数据库操作失败",
            operation="sqlalchemy_operation",
            details={"original_error": str(e)}
        )
    except Exception as e:
        session.rollback()
        logger.error(f"Unexpected error in database session: {str(e)}", exc_info=True)
        raise DatabaseError(
            message="数据库会话发生未知错误",
            operation="session_management",
            details={"original_error": str(e), "error_type": type(e).__name__}
        )
    finally:
        session.close()


# 用于测试数据库连接
def test_db_connection():
    """测试数据库连接"""
    try:
        from sqlalchemy import text
        with get_db() as db:
            # 使用通用的SQL查询语法
            result = db.execute(text("SELECT 1"))
            result.fetchone()
            logger.info("Database connection successful")
        return True
    except DatabaseError as e:
        logger.error(f"Database connection failed: {e.message}", extra={"details": e.details})
        return False
    except Exception as e:
        logger.error(f"Unexpected error during database connection test: {str(e)}", exc_info=True)
        raise ConfigurationError(
            message="数据库连接测试失败",
            config_key="database_connection",
            details={"original_error": str(e)}
        )
