import base64
import os
import threading
import logging
import random
from tkinter import Tk, Button, PhotoImage, Label, Entry, StringVar, N, E, \
    messagebox, scrolledtext, END, LabelFrame
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from configparser import ConfigParser

from images import img_icon
from images import img_logo

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S')

# define global variable
driver = None
running = None
interrupt = None

# load configparser
config = ConfigParser()
config.read('config.ini')


# logging handler
class TextHandler(logging.Handler):

    def __init__(self, text):
        # run the regular Handler __init__
        logging.Handler.__init__(self)
        # Store a reference to the Text it will log to
        self.text = text

    def emit(self, record):
        msg = self.format(record)

        def append():
            self.text.configure(state='normal')
            self.text.insert(END, msg + '\n')
            self.text.configure(state='disabled')
            # Autoscroll to the bottom
            self.text.yview(END)

        self.text.after(0, append)


# auto roll call
def auto_run():
    logging.info("--------啟動程序--------")
    global driver, running, interrupt
    interrupt = threading.Event()

    try:
        # setting browser
        options = Options()
        options.add_argument('--disable-gpu')
        options.add_argument("--proxy-server='direct://'")
        options.add_argument("--proxy-bypass-list=*")
        driver_path = config["path"]["chrome"]
        driver = webdriver.Chrome(executable_path=driver_path, options=options)
        # setting location
        params = {
            "latitude": float(config["location"]["latitude"]),
            "longitude": float(config["location"]["longitude"]),
            "accuracy": 100
        }
        driver.execute_cdp_cmd("Page.setGeolocationOverride", params)
    except:
        stop_func()
        logging.info("瀏覽器驅動錯誤，請確認下載驅動路徑正確")
        messagebox.showinfo("訊息", "瀏覽器驅動錯誤，請確認下載驅動路徑正確")
        logging.info("--------停止程序--------")
    else:
        login()


def login():
    global driver, running, interrupt
    # start simulation
    logging.info("進入登入頁面")
    driver.get(config["url"]["home_page"])
    driver.find_element(By.ID, "email").send_keys(config["user"]["account"])
    driver.find_element(By.ID, "password").send_keys(config["user"]["password"])
    driver.find_element(By.ID, "login_btn").submit()
    PageSource = driver.page_source
    soup = BeautifulSoup(PageSource, 'html.parser')
    result = soup.find(class_="msg_box")
    if "密碼錯誤" in str(result):
        logging.info("密碼錯誤")
        messagebox.showinfo("訊息", "密碼錯誤")
        running = False
    elif "查無此電子郵件" in str(result):
        logging.info("查無此電子郵件")
        messagebox.showinfo("訊息", "查無此電子郵件")
        running = False

    if running:
        logging.info("登入成功")
        driver.get(config["url"]["subject_page"])
        logging.info("開始點名")

    while running:
        PageSource = driver.page_source
        soup = BeautifulSoup(PageSource, 'html.parser')
        result = soup.find("div", class_="irs-rollcall")
        logging.debug(result)

        if "準時" in str(result):
            messagebox.showinfo("訊息", "已完成點名...")
            logging.info("已完成點名...")
            break

        elif "簽到開放中" in str(result):
            logging.info("點名中")
            driver.find_element(By.ID, "submit-make-rollcall").click()
            interrupt.wait(1)
            driver.find_element(By.CLASS_NAME, "button-box").click()
            messagebox.showinfo("訊息", "點名成功")
            logging.info("點名成功")
            break

        else:
            logging.info("無點名資訊")
            driver.refresh()

        interrupt.wait(timeout=random.randint(
            int(config["refresh"]["min"]),
            int(config["refresh"]["max"])
        ))

    logging.info("停止點名")
    driver.quit()
    running = False
    logging.info("--------停止程序--------")


def start_func():
    global running
    if not running:
        thread = threading.Thread(target=auto_run)
        thread.setDaemon(True)
        thread.start()
        running = True


def stop_func():
    global driver, running, interrupt
    if running:
        running = False
        interrupt.set()


def save_config():
    logging.info("開始儲存")
    global subject_page, account, password, latitude, longitude
    try:
        config["url"]["subject_page"] = subject_page.get()
        config["user"]["account"] = account.get()
        config["user"]["password"] = password.get()
        config["location"]["latitude"] = latitude.get()
        config["location"]["longitude"] = longitude.get()
        with open('config.ini', 'w') as configfile:
            config.write(configfile)
        messagebox.showinfo("訊息", "儲存完成")
        logging.info("儲存完成")
    except:
        messagebox.showinfo("訊息", "儲存失敗")
        logging.info("儲存失敗")


def about_message():
    messagebox.showinfo(
        "訊息",
        "本程式使用瀏覽器模擬與原始碼解析方法，針對固定網頁元件ID進行操作，"
        "因此若Zuvio網頁變更網頁原始碼，程式將會無法使用"
        "\n\n使用說明："
        "\n(1)先登入你的Zuvio選擇你要點名的課程"
        "\n(2)點擊進入\"點名簽到\"頁面"
        "\n(3)複製該網址並貼上到點名程式的\"點名網址\"，"
        "\n範例：https://irs.zuvio.com.tw/student5/irs/rollcall/510500"
        "\n(4)輸入你的Zuvio帳號密碼到點名程式內"
        "\n(5)去GoogleMap找到你的學校的經緯度並貼到點名程式內，若沒有GPS點名需求者此處可隨意填一個經緯度"
        "\n(6)按下儲存資料，完成用戶配置"
        "\n(7)按下啟動點名按鈕，程式將開啟一個模擬瀏覽器自動登入，並每隔一段時間刷新瀏覽器判斷是否有開啟點名"
        "\n(8)點名成功後會跳出完成視窗，點擊\"確定\"後點名瀏覽器將自動關閉"
        "\n\n按下\"停止點名\"按鈕可以停止自動點名程式並關閉點名瀏覽器"
        "\n\n免責聲明：本程式不負任何點名失敗造成之後果，請斟酌使用"
        "\n\n作者：YuCheng"
    )


def user_interface():
    windows = Tk()
    windows.title("Zuvio自動點名程式")
    windows.geometry("450x600")
    windows.resizable(width=0, height=0)

    global subject_page, account, password, latitude, longitude
    subject_page = StringVar()
    account = StringVar()
    password = StringVar()
    latitude = StringVar()
    longitude = StringVar()

    if not os.path.exists("config.ini"):
        init_config()

    subject_page.set(config["url"]["subject_page"])
    account.set(config["user"]["account"])
    password.set(config["user"]["password"])
    latitude.set(config["location"]["latitude"])
    longitude.set(config["location"]["longitude"])

    # make icon
    tmp = open("tmp.ico", "wb")
    tmp.write(base64.b64decode(img_icon))
    tmp.close()
    windows.iconbitmap('tmp.ico')
    os.remove("tmp.ico")

    # make logo
    tmp = open("tmp.ico", "wb")
    tmp.write(base64.b64decode(img_logo))
    tmp.close()
    logo = PhotoImage(file="tmp.ico")
    os.remove("tmp.ico")

    Label(windows, image=logo, height=120).grid(column=0, row=0, columnspan=2, padx=10, pady=5, sticky=N)

    button_frame = LabelFrame(windows, text="按鈕")
    button_frame.grid(row=1, column=0)

    Button(button_frame, text="啟動點名", command=start_func, width=28) \
        .grid(column=0, row=0, padx=5, pady=5, sticky=N)
    Button(button_frame, text="停止點名", command=stop_func, width=28) \
        .grid(column=1, row=0, padx=5, pady=5, sticky=N)
    Button(button_frame, text="使用說明", command=about_message, width=60) \
        .grid(column=0, row=1, columnspan=2, padx=10, pady=5, sticky=N)

    config_frame = LabelFrame(windows, text="配置")
    config_frame.grid(row=2, column=0)

    Label(config_frame, text="點名網址").grid(column=0, row=0, ipadx=5, pady=5, sticky=E + N)
    Entry(config_frame, textvariable=subject_page, width=50).grid(column=1, row=0, padx=10, pady=5, sticky=N)
    Label(config_frame, text="Zuvio帳號").grid(column=0, row=1, ipadx=5, pady=5, sticky=E + N)
    Entry(config_frame, textvariable=account, width=50).grid(column=1, row=1, padx=10, pady=5, sticky=N)
    Label(config_frame, text="Zuvio密碼").grid(column=0, row=2, ipadx=5, pady=5, sticky=E + N)
    Entry(config_frame, textvariable=password, width=50, show='*').grid(column=1, row=2, padx=10, pady=5, sticky=N)
    Label(config_frame, text="學校經度").grid(column=0, row=3, ipadx=5, pady=5, sticky=E + N)
    Entry(config_frame, textvariable=latitude, width=50).grid(column=1, row=3, padx=10, pady=5, sticky=N)
    Label(config_frame, text="學校緯度").grid(column=0, row=4, ipadx=5, pady=5, sticky=E + N)
    Entry(config_frame, textvariable=longitude, width=50).grid(column=1, row=4, padx=10, pady=5, sticky=N)

    Button(config_frame, text="儲存資料", command=save_config, width=60) \
        .grid(column=0, row=5, columnspan=2, padx=10, pady=5, sticky=N)

    logging_frame = LabelFrame(windows, text="紀錄")
    logging_frame.grid(row=3, column=0)

    st = scrolledtext.ScrolledText(logging_frame, width=50, height=7, state='disabled', font=('微軟正黑體', 10))
    st.grid(column=0, row=9, columnspan=2, padx=10, pady=5, sticky=N)

    text_handler = TextHandler(st)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s -  %(message)s')
    text_handler.setFormatter(formatter)

    logger = logging.getLogger()
    logger.addHandler(text_handler)

    windows.mainloop()


def init_config():
    logging.info("初始化 config.ini")
    config["url"] = {
        "home_page": "https://irs.zuvio.com.tw/",
        "subject_page": "https://irs.zuvio.com.tw/student5/irs/rollcall/510500"
    }
    config["user"] = {
        "account": "enter_account",
        "password": "enter_password"
    }
    config["location"] = {
        "latitude": "22.649803",
        "longitude": "120.328455"
    }
    config["refresh"] = {
        "min": "4",
        "max": "8"
    }
    config["path"] = {
        "chrome": "chromedriver.exe"
    }
    with open("config.ini", "w+") as configfile:
        config.write(configfile)
    logging.info("初始化完成")


if __name__ == "__main__":
    user_interface()
