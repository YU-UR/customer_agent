import logging
import os
from logging.handlers import TimedRotatingFileHandler
from typing import Optional
from pydantic import BaseModel, Field, DirectoryPath


class LogConfig(BaseModel):
    log_level: int = Field(default=logging.INFO, description="日志级别")
    base_log_dir: DirectoryPath = Field(
        default="logs", description="存放日志文件的基础目录"
    )
    rotation_time: str = Field(
        default="midnight", description="轮转时间，用于TimedRotatingFileHandler"
    )
    interval: int = Field(default=1, description="轮转的间隔单位数")
    backup_count: int = Field(
        default=30, description="保留的日志文件备份数量，默认保留30天"
    )
    log_format: str = Field(
        default="%(asctime)s | %(levelname)-8s | %(name)s:%(module)s:%(funcName)s:%(lineno)d - %(message)s",
        description="日志的格式",
    )

class LoggerUtil:
    """
    Logger Utility class that sets up logging for the entire Python project.
    Configured by the LogConfig settings.
    """
    def __init__(self, config: LogConfig):
        self.config = config
        os.makedirs(self.config.base_log_dir, exist_ok=True)

        # Configure the logger
        self.logger = logging.getLogger("ProjectLogger")
        self.logger.setLevel(self.config.log_level)

        # Add handlers only once to avoid duplicate logs
        if not self.logger.handlers:
            self._add_console_handler()
            self._add_file_handler()
        
        # Configure Uvicorn logs
        self._configure_uvicorn_logs()

    def _add_console_handler(self):
        """Add console handler to logger."""
        console_handler = logging.StreamHandler()
        console_handler.setLevel(self.config.log_level)
        console_handler.setFormatter(self._get_log_formatter())
        self.logger.addHandler(console_handler)

    def _add_file_handler(self):
        """Add file handler to logger with timed rotation."""
        log_path = os.path.join(self.config.base_log_dir, "app.log")
        file_handler = TimedRotatingFileHandler(
            log_path,
            when=self.config.rotation_time,
            interval=self.config.interval,
            backupCount=self.config.backup_count,
            encoding="utf-8"
        )
        file_handler.setLevel(self.config.log_level)
        file_handler.setFormatter(self._get_log_formatter())
        self.logger.addHandler(file_handler)

    def _get_log_formatter(self) -> logging.Formatter:
        """Define log format based on config."""
        return logging.Formatter(self.config.log_format, datefmt="%Y-%m-%d %H:%M:%S")

    def get_logger(self, name: Optional[str] = None) -> logging.Logger:
        """Get the configured logger."""
        return self.logger if name is None else self.logger.getChild(name)
    
    def _configure_uvicorn_logs(self):
        """Configure Uvicorn's loggers to use the project's logger."""
        for logger_name in ["uvicorn"]:
            uvicorn_logger = logging.getLogger(logger_name)
            uvicorn_logger.setLevel(self.config.log_level)

            if uvicorn_logger.handlers:
                uvicorn_logger.handlers.clear()
            
            # Add the handlers from the project logger
            for handler in self.logger.handlers:
                uvicorn_logger.addHandler(handler)


# Usage Example
log_config = LogConfig()
logger_util = LoggerUtil(config=log_config)