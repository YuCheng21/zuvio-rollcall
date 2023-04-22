import sys
from pathlib import Path
import logging
from logging.handlers import RotatingFileHandler

from PySide6.QtGui import QTextCursor


class GuiHandler(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:
        self.edit.textCursor().insertText(self.format(record) + '\n')
        self.edit.moveCursor(QTextCursor.End)


def get_logger():
    logger = logging.getLogger(__name__)
    # the logger with handler will use higher one level (!important)
    logger.setLevel(logging.DEBUG)
    return logger


def console_logger():
    console_handler = logging.StreamHandler(sys.stderr)
    console_format = logging.Formatter(
        fmt='%(asctime)s %(levelname)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_format)
    console_handler.setLevel(logging.DEBUG)
    return console_handler


def file_logger(output_path=None):
    assert output_path is not None
    log_path = Path(output_path)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    file_handler = RotatingFileHandler(log_path, maxBytes=1 * 10 ** 6, backupCount=10, encoding='UTF-8', delay=False)
    file_format = logging.Formatter(
        fmt='%(asctime)s %(levelname)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_format)
    file_handler.setLevel(logging.DEBUG)
    return file_handler


def gui_logger(edit):
    gui_handler = GuiHandler()
    formatter = logging.Formatter(
        fmt='%(asctime)s %(levelname)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
    )
    gui_handler.setLevel(logging.INFO)
    gui_handler.setFormatter(formatter)
    gui_handler.edit = edit
    return gui_handler
