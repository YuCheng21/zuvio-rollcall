import sys
from pathlib import Path
import time
import random

from PySide6.QtCore import QFile, QIODevice, QThreadPool, QRunnable, Signal
from PySide6.QtGui import QIcon
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QApplication, QTextEdit, QPushButton, QLineEdit, QCheckBox, QMessageBox
import qdarkstyle

from settings import Settings, StatusCode, read_args, save_args
from logger import get_logger, console_logger, file_logger, gui_logger
from web_crawler import Zuvio


class Script(QRunnable):
    def __init__(self, args):
        super().__init__()
        self.args = args
        self.code = StatusCode()
        self.status = Signal(str)
        self.stop()

    def log_script(func):
        def wrapper(*args, **kwargs):
            self = args[0]
            logger.info('----------開始點名----------')
            self.start()
            try:
                func(*args, **kwargs)
            except Exception as e:
                logger.error(e)
            finally:
                logger.info('----------結束點名----------')
                self.stop()

        wrapper.__name__ = func.__name__
        return wrapper

    def stop(self):
        self.status = self.code.stop

    def start(self):
        self.status = self.code.running

    @log_script
    def run(self):
        with Zuvio(self.args) as zuvio:
            logger.info('登入帳號')
            zuvio.login()
            logger.info('登入成功')
            while self.status == self.code.running:
                code = zuvio.check_in()
                if code == zuvio.code.finish:
                    logger.info('點名成功')
                    break
                logger.info('尚未點名')
                time.sleep(random.randint(self.args.refresh_min, self.args.refresh_max))


class UserInterface:
    def __init__(self):
        self.args = Settings()
        yaml_args = read_args(self.args.env_file)
        self.args = Settings(**yaml_args)

        self.code = StatusCode()

        ui_file = QFile(self.args.app_file)
        if not ui_file.open(QIODevice.ReadOnly):
            logger.error(f'Cannot open {self.args.app_file}: {ui_file.errorString()}')
            sys.exit(-1)

        loader = QUiLoader()
        self.window = loader.load(ui_file)
        ui_file.close()
        if not self.window:
            logger.error(loader.errorString())
            sys.exit(-1)

        self.script = Script(self.args)
        self.threadpool = QThreadPool()

    def find_child(self):
        self.btn_save: QPushButton = self.window.findChild(QPushButton, 'btn_save')
        self.btn_start: QPushButton = self.window.findChild(QPushButton, 'btn_start')
        self.btn_stop: QPushButton = self.window.findChild(QPushButton, 'btn_stop')
        self.btn_about: QPushButton = self.window.findChild(QPushButton, 'btn_about')

        self.edit_url: QLineEdit = self.window.findChild(QLineEdit, 'edit_url')
        self.edit_account: QLineEdit = self.window.findChild(QLineEdit, 'edit_account')
        self.edit_password: QLineEdit = self.window.findChild(QLineEdit, 'edit_password')
        self.edit_latitude: QLineEdit = self.window.findChild(QLineEdit, 'edit_latitude')
        self.edit_longitude: QLineEdit = self.window.findChild(QLineEdit, 'edit_longitude')
        self.edit_logging: QTextEdit = self.window.findChild(QTextEdit, 'edit_logging')

        self.check_headless: QCheckBox = self.window.findChild(QCheckBox, 'checkBox')

        return 0

    def initialize(self):
        self.edit_url.setText(self.args.url.target)
        self.edit_account.setText(self.args.user.account)
        self.edit_password.setText(self.args.user.password)
        self.edit_latitude.setText(str(self.args.location.latitude))
        self.edit_longitude.setText(str(self.args.location.longitude))
        self.check_headless.setChecked(self.args.headless)
        return 0

    def connect(self):
        self.btn_save.clicked.connect(self.save)
        self.btn_start.clicked.connect(self.start)
        self.btn_stop.clicked.connect(self.stop)
        self.btn_about.clicked.connect(self.about)
        return 0

    def save(self):
        self.args.url.target = self.edit_url.text()
        self.args.user.account = self.edit_account.text()
        self.args.user.password = self.edit_password.text()
        self.args.location.latitude = self.edit_latitude.text()
        self.args.location.longitude = self.edit_longitude.text()
        self.args.headless = self.check_headless.isChecked()
        self.args = Settings(**self.args.dict())
        try:
            save_args(self.args.dict(), self.args.env_file)
        except Exception as e:
            logger.error(e)
            QMessageBox.critical(self.window, '錯誤', '儲存失敗', QMessageBox.Ok)
        else:
            logger.info('儲存完成')
            QMessageBox.information(self.window, '完成', '儲存完成', QMessageBox.Ok)
        return 0

    def start(self):
        self.save()
        if hasattr(self, 'script') is True:
            if self.script.status == self.code.running:
                return 1
            elif self.script.status == self.code.stop:
                self.script = Script(self.args)
        self.threadpool.start(self.script)
        return 0

    def stop(self):
        if self.script.status == self.code.stop:
            return 1
        logger.info('中斷點名')
        self.script.stop()
        return 0

    def about(self):
        with open('about.txt', 'r', encoding='utf-8') as f:
            data = f.read()
        QMessageBox.information(self.window, 'Info', data, QMessageBox.Ok)
        return 0


if __name__ == '__main__':
    icon_path = './static/icon.ico'
    log_path = './logs/app.logs'

    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(icon_path))

    # setup stylesheet
    app.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyside6', palette=qdarkstyle.LightPalette))

    gui = UserInterface()
    gui.find_child()
    gui.initialize()
    gui.connect()

    logger = get_logger()
    logger.addHandler(console_logger())
    logger.addHandler(file_logger(Path(log_path)))
    logger.addHandler(gui_logger(gui.edit_logging))

    gui.window.show()
    sys.exit(app.exec())
