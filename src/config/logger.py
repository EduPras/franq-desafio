import logging
from logging import Logger
from pathlib import Path

from rich.console import Console
from rich.logging import RichHandler


class LoggerBuilder:
    DEFAUlT_LOG_PATH = Path("logs")

    def __init__(
            self, name, level, stream_handler=True, file_handler=False
    ) -> None:
        self.name = name
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)

        if stream_handler:
            stream_handler = RichHandler(
                console=Console(stderr=True),
                show_time=True,
                show_level=True,
                show_path=True,
                markup=True,
            )
            stream_handler.setLevel(level)
            self.logger.addHandler(stream_handler)

        if file_handler:
            path = self.DEFAUlT_LOG_PATH / f"{self.name}.log"
            file_handler = logging.FileHandler(path)
            file_handler.setLevel(level)
            self.logger.addHandler(file_handler)

    def getLogger(self) -> Logger:
        return self.logger
