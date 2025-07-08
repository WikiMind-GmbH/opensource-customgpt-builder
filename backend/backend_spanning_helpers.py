import os


def require_env(name: str) -> str:
    value = os.getenv(name)
    if value is None:
        raise RuntimeError(f'Missing required environment variable: {name}')
    return value
