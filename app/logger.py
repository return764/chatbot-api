import logging
import sys

# 定义颜色代码
class ColorFormatter(logging.Formatter):
    green = "\x1b[32m"
    yellow = "\x1b[33m"
    red = "\x1b[31m"
    reset = "\x1b[0m"
    grey = "\x1b[38;5;244m"
    
    def format(self, record):
        color = {
            'INFO': self.green,
            'WARNING': self.yellow,
            'ERROR': self.red,
            'DEBUG': self.grey
        }.get(record.levelname, self.reset)
        
        record.levelname = f'{color}{record.levelname:<8}{self.reset}'
        return super().format(record)

# uvicorn日志配置
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "colored": {
            "()": "app.logger.ColorFormatter",
            "fmt": "[%(asctime)s] %(levelname)s %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        }
    },
    "handlers": {
        "default": {
            "formatter": "colored",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        }
    },
    "loggers": {
        "uvicorn": {
            "handlers": ["default"],
            "level": "INFO",
            "propagate": False
        },
        "uvicorn.error": {
            "handlers": ["default"],
            "level": "INFO",
            "propagate": False
        },
        "uvicorn.access": {
            "handlers": ["default"],
            "level": "INFO",
            "propagate": False
        },
    }
} 