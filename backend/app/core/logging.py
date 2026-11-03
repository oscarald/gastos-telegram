import logging
import sys

_CONFIGURED = False


def configure_logging(level: str | None = None) -> None:
    """Configura logging basico en stdout (compatible con Docker)."""
    global _CONFIGURED
    if _CONFIGURED:
        return

    from app.core.config import get_settings

    resolved = (level or get_settings().log_level or "INFO").upper()
    logging.basicConfig(
        stream=sys.stdout,
        level=getattr(logging, resolved, logging.INFO),
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        force=True,
    )
    _CONFIGURED = True


def get_logger(name: str) -> logging.Logger:
    configure_logging()
    return logging.getLogger(name)
