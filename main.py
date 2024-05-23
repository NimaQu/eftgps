import configparser
import logging
import os
import sys
import time

from selenium import webdriver
from selenium.common import TimeoutException, NoSuchWindowException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.wait import WebDriverWait
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
from webdriver_manager.chrome import ChromeDriverManager

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', encoding="utf-8")
config = configparser.ConfigParser()
config.read("config.ini", encoding="utf-8")
input_box: WebElement = None


class MyHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory:
            file_name = os.path.basename(event.src_path)
            file_name_without_extension = os.path.splitext(file_name)[0]
            send_file_name_to_input_box(file_name_without_extension)


def send_file_name_to_input_box(file_name: str):
    global input_box
    if input_box is None:
        raise ValueError("error: input_box is not set")
    input_box.clear()
    input_box.send_keys(file_name)


def main(game_map: str):
    global input_box
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    path = config.get("DEFAULT", "ScreenShotPath", fallback=None)
    loading_delay = config.getint("DEFAULT", "LoadingDelay", fallback=5)
    if path is None or path == "":
        raise ValueError("截图路径未设置")
    logging.info(f"截图路径设定为: {path}")
    event_handler = MyHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=False)
    driver.get(f'https://tarkov-market.com/maps/{game_map}')

    WebDriverWait(driver, 10).until(
        lambda _driver: driver.execute_script("return document.readyState") == "complete"
    )

    time.sleep(loading_delay)
    logging.info(f"等待{loading_delay}秒页面加载完成...")

    try:
        # 全屏按钮
        full_screen_button = WebDriverWait(driver, 10).until(
            lambda _driver: driver.find_element(By.XPATH, '//button[text()="Full screen"]')
        )
        full_screen_button.click()
        logging.info("设定为全屏模式")
        # 隐藏面板按钮
        hide_button = WebDriverWait(driver, 10).until(
            lambda _driver: driver.find_element(By.XPATH, '//button[text()="Hide pannels"]')
        )
        hide_button.click()
        logging.info("隐藏面板")
        # 查找按钮
        button = WebDriverWait(driver, 10).until(
            lambda _driver: driver.find_element(By.XPATH, '//button[text()="Where am i?"]')
        )
        button.click()
        logging.info("点击按钮")
        # 等待按钮点击后的效果加载完成
        time.sleep(1)
        # 定位具有特定 placeholder 的输入框
        input_box = WebDriverWait(driver, 10).until(
            lambda _driver: driver.find_element(By.XPATH, '//input[@placeholder="Paste file name here"]')
        )
    except TimeoutException:
        logging.error("页面元素加载超时")
        driver.quit()
        return

    logging.info("准备完毕，开始监听截图文件夹...")
    observer.start()

    while True:
        try:
            # 检测窗口是否关闭
            handle = driver.current_window_handle
            time.sleep(1)
        except NoSuchWindowException:
            logging.info("浏览器窗口关闭，程序结束")
            observer.stop()
            observer.join(timeout=1)
            driver.quit()
            logging.info("程序结束")
            break


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("请传入地图名称参数， 如：main.py ground-zero")
        sys.exit(1)
    try:
        main(game_map=sys.argv[1])
    except KeyboardInterrupt:
        print("程序结束")
    except Exception as e:
        logging.error(e)
        print("程序异常结束")
