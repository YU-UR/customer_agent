"""
系统配置管理
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, validator
from typing import Optional
import os
import logging

from .exceptions import ConfigurationError

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """应用配置类"""
    
    # 应用基础配置
    APP_NAME: str = "智能电商客服与销售支持系统"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"

    # 服务器配置
    HOST: str = "0.0.0.0"
    PORT: int = 8001
    
    # 数据库配置
    MYSQL_HOST: str = Field(default="localhost", description="MySQL主机地址")
    MYSQL_PORT: int = Field(default=3306, ge=1, le=65535, description="MySQL端口")
    MYSQL_USER: str = Field(default="root", min_length=1, description="MySQL用户名")
    MYSQL_PASSWORD: str = Field(default="", description="MySQL密码")
    MYSQL_DATABASE: str = Field(default="customer_service", min_length=1, description="MySQL数据库名")
    
    # Redis配置
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: Optional[str] = None
    REDIS_DB: int = 0
    
    # Milvus配置
    MILVUS_URL: str = "http://127.0.0.1:19530"
    COLLECTION_NAME: str = "customer_service"
    DIMENSION: int = 1536
    
    # JWT配置
    SECRET_KEY: str = "your-secret-key-here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # AI模型配置
    OPENAI_API_KEY: Optional[str] = Field(default="", description="OpenAI API密钥")
    OPENAI_BASE_URL: Optional[str] = Field(default="https://api.deepseek.com/v1", description="OpenAI API基础URL")
    MODEL_NAME: str = Field(default="deepseek-chat", min_length=1, description="AI模型名称")

    # MEM0长期记忆框架配置
    MODEL_PROVIDER: str = "deepseek"
# 嵌入模型配置
    EMBEDDING_PROVIDER: str = "openai"
    EMBEDDING_MODEL: str = "text-embedding-v4"
    EMBEDDING_BASE_URL: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    EMBEDDING_API_KEY: str = ""


    VECTOR_PROVIDER: str = "milvus"
    # MCP_SERVER服务地址
    MCP_URL: Optional[str] = "http://127.0.0.1:8000/sse"
    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/app.log"
    
    @validator('OPENAI_API_KEY')
    def validate_openai_api_key(cls, v):
        """验证OpenAI API密钥"""
        if v and len(v.strip()) < 10:
            raise ValueError("OpenAI API密钥长度不能少于10个字符")
        return v
    
    @validator('OPENAI_BASE_URL')
    def validate_openai_base_url(cls, v):
        """验证OpenAI API基础URL"""
        if v and not v.startswith(('http://', 'https://')):
            raise ValueError("OpenAI API基础URL必须以http://或https://开头")
        return v
    
    @validator('MILVUS_URL')
    def validate_milvus_url(cls, v):
        """验证Milvus URL"""
        if not v.startswith(('http://', 'https://')):
            raise ValueError("Milvus URL必须以http://或https://开头")
        return v
    
    @validator('SECRET_KEY')
    def validate_secret_key(cls, v):
        """验证JWT密钥"""
        if len(v) < 32:
            logger.warning("JWT密钥长度建议至少32个字符以确保安全性")
        return v

    @property
    def mysql_url(self) -> str:
        """MySQL数据库连接URL"""
        try:
            return f"mysql+pymysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}"
        except Exception as e:
            raise ConfigurationError(
                message="MySQL连接URL构建失败",
                config_key="mysql_url",
                details={"error": str(e)}
            )

    @property
    def redis_url(self) -> str:
        """Redis连接URL"""
        try:
            if self.REDIS_PASSWORD:
                return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
            return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        except Exception as e:
            raise ConfigurationError(
                message="Redis连接URL构建失败",
                config_key="redis_url",
                details={"error": str(e)}
            )
    
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True, extra="ignore")


def validate_settings() -> None:
    """验证配置设置"""
    try:
        # 检查必要的环境变量
        required_env_vars = ['OPENAI_API_KEY', 'EMBEDDING_API_KEY']
        missing_vars = []
        
        for var in required_env_vars:
            value = getattr(settings, var, None)
            if not value or value.strip() == "":
                missing_vars.append(var)
        
        if missing_vars:
            logger.warning(f"以下环境变量未设置或为空: {', '.join(missing_vars)}")
        
        # 验证数据库连接URL
        try:
            mysql_url = settings.mysql_url
            logger.info("MySQL连接URL验证通过")
        except Exception as e:
            raise ConfigurationError(
                message="MySQL配置验证失败",
                config_key="mysql_config",
                details={"error": str(e)}
            )
        
        # 验证Redis连接URL
        try:
            redis_url = settings.redis_url
            logger.info("Redis连接URL验证通过")
        except Exception as e:
            raise ConfigurationError(
                message="Redis配置验证失败",
                config_key="redis_config",
                details={"error": str(e)}
            )
        
        logger.info("配置验证完成")
        
    except Exception as e:
        logger.error(f"配置验证失败: {str(e)}")
        raise


# 全局配置实例
try:
    settings = Settings()
    # 在导入时进行基本验证
    validate_settings()
except Exception as e:
    logger.error(f"配置初始化失败: {str(e)}")
    raise ConfigurationError(
        message="系统配置初始化失败",
        config_key="settings_initialization",
        details={"error": str(e)}
    )