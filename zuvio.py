import base64
import os
import threading
import logging
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from configparser import ConfigParser
from webdriver_manager.chrome import ChromeDriverManager
from tkinter import Tk, Button, PhotoImage, Label, Entry, StringVar, N, E, \
    messagebox, scrolledtext, END, LabelFrame

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


def init_web():
    global driver, running, interrupt
    save_config()
    logging.info("--------εεη¨εΊ--------")
    interrupt = threading.Event()

    try:
        # setting browser
        options = Options()
        options.add_argument('--disable-gpu')
        options.add_argument("--proxy-server='direct://'")
        options.add_argument("--proxy-bypass-list=*")

        driver = webdriver.Chrome(executable_path=ChromeDriverManager().install(), options=options)
        # setting location
        params = {
            "latitude": float(config["location"]["latitude"]),
            "longitude": float(config["location"]["longitude"]),
            "accuracy": 100
        }
        driver.execute_cdp_cmd("Page.setGeolocationOverride", params)
    except Exception as e:
        stop_func()
        logging.exception(e)
        logging.info("ηθ¦½ε¨ι©ει―θͺ€οΌθ«η’ΊθͺδΈθΌι©εθ·―εΎζ­£η’Ί")
        messagebox.showinfo("θ¨ζ―", "ηθ¦½ε¨ι©ει―θͺ€οΌθ«η’ΊθͺδΈθΌι©εθ·―εΎζ­£η’Ί")
        logging.info("--------εζ­’η¨εΊ--------")
    else:
        login()


def login():
    global driver, running, interrupt
    # start simulation
    logging.info("ι²ε₯η»ε₯ι ι’")
    driver.get(config["url"]["home_page"])
    driver.find_element(By.ID, "email").send_keys(config["user"]["account"])
    driver.find_element(By.ID, "password").send_keys(config["user"]["password"])
    driver.find_element(By.ID, "login_btn").submit()

    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')
    result = soup.find(class_="msg_box")
    if "ε―η’Όι―θͺ€" in str(result):
        logging.info("ε―η’Όι―θͺ€")
        messagebox.showinfo("θ¨ζ―", "ε―η’Όι―θͺ€")
        running = False
    elif "ζ₯η‘ζ­€ι»ε­ι΅δ»Ά" in str(result):
        logging.info("ζ₯η‘ζ­€ι»ε­ι΅δ»Ά")
        messagebox.showinfo("θ¨ζ―", "ζ₯η‘ζ­€ι»ε­ι΅δ»Ά")
        running = False

    if running:
        logging.info("η»ε₯ζε")
        driver.get(config["url"]["subject_page"])
        logging.info("ιε§ι»ε")

    roll_call()


def roll_call():
    global driver, running, interrupt
    while running:
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        result = soup.find("div", class_="irs-rollcall")
        logging.debug(result)

        if "ζΊζ" in str(result):
            messagebox.showinfo("θ¨ζ―", "ε·²ε?ζι»ε...")
            logging.info("ε·²ε?ζι»ε...")
            break

        elif "η°½ε°ιζΎδΈ­" in str(result):
            logging.info("ι»εδΈ­")
            driver.find_element(By.ID, "submit-make-rollcall").click()
            interrupt.wait(1)
            driver.find_element(By.CLASS_NAME, "button-box").click()
            messagebox.showinfo("θ¨ζ―", "ι»εζε")
            logging.info("ι»εζε")
            break

        else:
            logging.info("η‘ι»εθ³θ¨")
            driver.refresh()

        interrupt.wait(timeout=random.randint(
            int(config["refresh"]["min"]),
            int(config["refresh"]["max"])
        ))

    logging.info("εζ­’ι»ε")
    driver.quit()
    running = False
    logging.info("--------εζ­’η¨εΊ--------")


def start_func():
    global running
    if not running:
        thread = threading.Thread(target=init_web)
        thread.setDaemon(True)
        thread.start()
        running = True


def stop_func():
    global driver, running, interrupt
    if running:
        running = False
        interrupt.set()


def save_config():
    logging.info("ιε§ε²ε­")
    global subject_page, account, password, latitude, longitude
    try:
        config["url"]["subject_page"] = subject_page.get()
        config["user"]["account"] = account.get()
        config["user"]["password"] = password.get()
        config["location"]["latitude"] = latitude.get()
        config["location"]["longitude"] = longitude.get()
        with open('config.ini', 'w') as configfile:
            config.write(configfile)
        logging.info("ε²ε­ε?ζ")
    except:
        logging.info("ε²ε­ε€±ζ")


def about_message():
    messagebox.showinfo(
        "θ¨ζ―",
        "ζ¬η¨εΌδ½Ώη¨ηθ¦½ε¨ζ¨‘ζ¬θεε§η’Όθ§£ζζΉζ³οΌιε°εΊε?ηΆ²ι εδ»ΆIDι²θ‘ζδ½οΌ"
        "ε ζ­€θ₯ZuvioηΆ²ι θ?ζ΄ηΆ²ι εε§η’ΌοΌη¨εΌε°ζη‘ζ³δ½Ώη¨"
        "\n\nδ½Ώη¨θͺͺζοΌ"
        "\n(1)εη»ε₯δ½ ηZuvioιΈζδ½ θ¦ι»εηθͺ²η¨"
        "\n(2)ι»ζι²ε₯\"ι»εη°½ε°\"ι ι’"
        "\n(3)θ€θ£½θ©²ηΆ²εδΈ¦θ²ΌδΈε°ι»εη¨εΌη\"ι»εηΆ²ε\"οΌ"
        "\nη―δΎοΌhttps://irs.zuvio.com.tw/student5/irs/rollcall/510500"
        "\n(4)θΌΈε₯δ½ ηZuvioεΈ³θε―η’Όε°ι»εη¨εΌε§"
        "\n(5)ε»GoogleMapζΎε°δ½ ηε­Έζ ‘ηηΆη·―εΊ¦δΈ¦θ²Όε°ι»εη¨εΌε§οΌθ₯ζ²ζGPSι»ειζ±θζ­€θε―ι¨ζε‘«δΈεηΆη·―εΊ¦"
        "\n(6)ζδΈε²ε­θ³ζοΌε?ζη¨ζΆιη½?"
        "\n(7)ζδΈεει»εζιοΌη¨εΌε°ιεδΈεζ¨‘ζ¬ηθ¦½ε¨θͺεη»ε₯οΌδΈ¦ζ―ιδΈζ?΅ζιε·ζ°ηθ¦½ε¨ε€ζ·ζ―ε¦ζιει»ε"
        "\n(8)ι»εζεεΎζθ·³εΊε?ζθ¦ηͺοΌι»ζ\"η’Ίε?\"εΎι»εηθ¦½ε¨ε°θͺειι"
        "\n\nζδΈ\"εζ­’ι»ε\"ζιε―δ»₯εζ­’θͺει»εη¨εΌδΈ¦ιιι»εηθ¦½ε¨"
        "\n\nεθ²¬θ²ζοΌζ¬η¨εΌδΈθ² δ»»δ½ι»εε€±ζι ζδΉεΎζοΌθ«ζιδ½Ώη¨"
        "\n\nδ½θοΌYuCheng"
    )


def user_interface():
    windows = Tk()
    windows.title("Zuvioθͺει»εη¨εΌ")
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

    button_frame = LabelFrame(windows, text="ζι")
    button_frame.grid(row=1, column=0)

    Button(button_frame, text="εει»ε", command=start_func, width=28) \
        .grid(column=0, row=0, padx=5, pady=5, sticky=N)
    Button(button_frame, text="εζ­’ι»ε", command=stop_func, width=28) \
        .grid(column=1, row=0, padx=5, pady=5, sticky=N)
    Button(button_frame, text="δ½Ώη¨θͺͺζ", command=about_message, width=60) \
        .grid(column=0, row=1, columnspan=2, padx=10, pady=5, sticky=N)

    config_frame = LabelFrame(windows, text="ιη½?")
    config_frame.grid(row=2, column=0)

    Label(config_frame, text="ι»εηΆ²ε").grid(column=0, row=0, ipadx=5, pady=5, sticky=E + N)
    Entry(config_frame, textvariable=subject_page, width=50).grid(column=1, row=0, padx=10, pady=5, sticky=N)
    Label(config_frame, text="ZuvioεΈ³θ").grid(column=0, row=1, ipadx=5, pady=5, sticky=E + N)
    Entry(config_frame, textvariable=account, width=50).grid(column=1, row=1, padx=10, pady=5, sticky=N)
    Label(config_frame, text="Zuvioε―η’Ό").grid(column=0, row=2, ipadx=5, pady=5, sticky=E + N)
    Entry(config_frame, textvariable=password, width=50, show='*').grid(column=1, row=2, padx=10, pady=5, sticky=N)
    Label(config_frame, text="ε­Έζ ‘ηΆεΊ¦").grid(column=0, row=3, ipadx=5, pady=5, sticky=E + N)
    Entry(config_frame, textvariable=latitude, width=50).grid(column=1, row=3, padx=10, pady=5, sticky=N)
    Label(config_frame, text="ε­Έζ ‘η·―εΊ¦").grid(column=0, row=4, ipadx=5, pady=5, sticky=E + N)
    Entry(config_frame, textvariable=longitude, width=50).grid(column=1, row=4, padx=10, pady=5, sticky=N)

    Button(config_frame, text="ε²ε­θ³ζ", command=save_config, width=60) \
        .grid(column=0, row=5, columnspan=2, padx=10, pady=5, sticky=N)

    logging_frame = LabelFrame(windows, text="θ¨ι")
    logging_frame.grid(row=3, column=0)

    st = scrolledtext.ScrolledText(logging_frame, width=50, height=7, state='disabled', font=('εΎ?θ»ζ­£ι»ι«', 10))
    st.grid(column=0, row=9, columnspan=2, padx=10, pady=5, sticky=N)

    text_handler = TextHandler(st)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s -  %(message)s')
    text_handler.setFormatter(formatter)

    logger = logging.getLogger()
    logger.addHandler(text_handler)

    windows.mainloop()


def init_config():
    logging.info("εε§ε config.ini")
    config["url"] = {
        "home_page": "https://irs.zuvio.com.tw/",
        "subject_page": "https://irs.zuvio.com.tw/student5/irs/rollcall/123456"
    }
    config["user"] = {
        "account": "1234567890@school.edu.tw",
        "password": "enter-password"
    }
    config["location"] = {
        "latitude": "22.649803",
        "longitude": "120.328455"
    }
    config["refresh"] = {
        "min": "4",
        "max": "8"
    }
    with open("config.ini", "w+") as configfile:
        config.write(configfile)
    logging.info("εε§εε?ζ")


if __name__ == "__main__":
    user_interface()
