import logging.config
from enum import StrEnum


class LoggerContext(StrEnum):
    CUSTOMGPTS = "customgpts"
    CHAT = "chat"
    KNOWLEDGE = "knowledge"


def get_logger(
    context: LoggerContext,
    component: str,
) -> logging.Logger:
    if not component:
        raise ValueError("Logger component must not be empty")

    return logging.getLogger(f"{context}.{component}")


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
                    "format": "%(asctime)s %(levelname)s [%(name)s] %(message)s",
                    "datefmt": "%H:%M:%S",
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
            },
        }
    )
