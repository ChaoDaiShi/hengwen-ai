import logging


def configure_logging(level: str) -> None:
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format=(
            "%(asctime)s %(levelname)s %(name)s request_id=%(request_id)s %(message)s"
        ),
    )
