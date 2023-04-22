import random
from pathlib import Path
import time
import os

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup as bs

from settings import ZuvioCode


class Zuvio:
    def __init__(self, args):
        self.args = args
        self.code = ZuvioCode()
        os.environ["WDM_PROGRESS_BAR"] = "0"

    def __enter__(self):
        self.driver = self.get_driver()
        self.driver.implicitly_wait(10)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.driver.quit()

    def get_driver(self):
        driver_path = Path('./driver')
        driver_path.mkdir(parents=True, exist_ok=True)
        options = {
            'version': '111.0.5563.64',
            'path': str(driver_path.absolute())
        }
        service = ChromeService(ChromeDriverManager(**options).install())
        options = Options()
        options.add_argument('--disable-gpu')
        options.add_argument("--proxy-server='direct://'")
        options.add_argument("--proxy-bypass-list=*")
        options.add_argument("--headless=new") if self.args.headless is True else 0
        driver = webdriver.Chrome(service=service, options=options)
        params = {
            "latitude": self.args.location.latitude,
            "longitude": self.args.location.longitude,
            "accuracy": 100
        }
        driver.execute_cdp_cmd("Page.setGeolocationOverride", params)
        return driver

    def login(self):
        self.driver.get(self.args.url.home)
        self.driver.find_element(By.CSS_SELECTOR, '#email').send_keys(self.args.user.account)
        self.driver.find_element(By.CSS_SELECTOR, '#password').send_keys(self.args.user.password)
        self.driver.find_element(By.CSS_SELECTOR, '#login-btn').click()
        element = bs(self.driver.page_source, 'html.parser').select('#myform > div.msg_box > div.err_msg')
        if len(element) > 0:
            raise Exception(self.code.login_failed, self.code.login_failed)
        return 0

    def check_in(self):
        self.driver.get(self.args.url.target)
        element = bs(self.driver.page_source, 'html.parser').select('#content > div.irs-rollcall > div.i-r-footer-box > div')
        if len(element) == 0:
            return self.code.waiting
        element = element[0]
        if element.text == '我到了':
            self.driver.find_element(By.CSS_SELECTOR, '#submit-make-rollcall').click()
            return self.code.starting
        return self.code.finish


if __name__ == '__main__':
    from settings import Settings
    args = Settings()

    with Zuvio(args) as zuvio:
        zuvio.login()
        while True:
            code = zuvio.check_in()
            if code == zuvio.code.finish:
                break
            else:
                time.sleep(random.randint(args.refresh_min, args.refresh_max))
