import pytest

from src.runtime.logging import configure_logging


@pytest.fixture(autouse=True)
def configure_test_logging():
    configure_logging()


# caplog.set_level(logging.WARNING)

# for logger_name in PROJECT_DEBUG_LOGGER_PREFIXES:
#     caplog.set_level(logging.DEBUG, logger=logger_name)
