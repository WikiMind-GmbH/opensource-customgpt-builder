import logging.config
from enum import StrEnum


class LoggerContext(StrEnum):
    CUSTOMGPTS = "customgpts"
    CHAT = "chat"
    KNOWLEDGE = "knowledge"
    INTERFACE = "interface"


class HealthcheckFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        return "/maintenance/healthz" not in record.getMessage()


def get_logger(
    context: LoggerContext,
    component: str,
) -> logging.Logger:
    if not component:
        raise ValueError("Logger component must not be empty")

    return logging.getLogger(f"{context}.{component}")


class ColorLevelFormatter(logging.Formatter):
    RESET = "\033[0m"

    COLORS = {
        logging.DEBUG: "\033[90m",  # gray
        logging.INFO: "\033[32m",  # green
        logging.WARNING: "\033[33m",  # yellow
        logging.ERROR: "\033[31m",  # red
        logging.CRITICAL: "\033[1;31m",  # bold red
    }

    def format(self, record: logging.LogRecord) -> str:
        original_levelname = record.levelname

        color = self.COLORS.get(record.levelno, "")
        record.levelname = f"{color}{record.levelname}{self.RESET}"

        try:
            return super().format(record)
        finally:
            record.levelname = original_levelname


def configure_logging() -> None:
    root_log_level = "WARNING"
    knowledge_log_level = "DEBUG"
    chat_log_level = "DEBUG"
    customgpts_log_level = "DEBUG"

    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "()": ColorLevelFormatter,
                    "format": "%(asctime)s %(levelname)s [%(name)s]:    %(message)s",
                    "datefmt": "%H:%M:%S",
                },
            },
            "filters": {
                "ignore_healthcheck": {
                    "()": HealthcheckFilter,
                },
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "default",
                },
            },
            "root": {
                "handlers": ["console"],
                "level": root_log_level,
            },
            "loggers": {
                "uvicorn.access": {
                    "filters": [
                        "ignore_healthcheck"
                    ],  # we don't want to see the logs of the healthcheck polluting our INFO logs
                    "propagate": True,
                },
                LoggerContext.KNOWLEDGE.value: {
                    "level": knowledge_log_level,
                    "propagate": True,
                },
                LoggerContext.CHAT.value: {
                    "level": chat_log_level,
                    "propagate": True,
                },
                LoggerContext.CUSTOMGPTS.value: {
                    "level": customgpts_log_level,
                    "propagate": True,
                },
                LoggerContext.INTERFACE.value: {
                    "level": customgpts_log_level,
                    "propagate": True,
                },
            },
        }
    )
