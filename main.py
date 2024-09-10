import configparser
import logging
import os
import time
import argparse

from selenium import webdriver
from selenium.common import TimeoutException, NoSuchWindowException, StaleElementReferenceException
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.chrome import ChromeDriverManager


logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', encoding="utf-8")
config = configparser.ConfigParser()
config.read("config.ini", encoding="utf-8")


class MyHandler(FileSystemEventHandler):
    def __init__(self, driver, loading_delay):
        self.driver = driver
        self.loading_delay = loading_delay

    def on_created(self, event):
        if not event.is_directory:
            file_name = os.path.basename(event.src_path)
            file_name_without_extension = os.path.splitext(file_name)[0]
            print(file_name_without_extension)
            self.send_file_name_to_input_box(file_name_without_extension)
            try:
                os.remove(event.src_path)
            except FileNotFoundError:
                pass
            except PermissionError:
                logging.error(f"无法删除文件: {event.src_path}")

    def send_file_name_to_input_box(self, file_name: str):
        if self.input_box is None:
            raise ValueError("error: input_box is not set")
        try:
            self.input_box.clear()
            self.input_box.send_keys(file_name)
        except StaleElementReferenceException:
            self.find_button()

    def page_init(self):
        try:
            WebDriverWait(self.driver, 10).until(
                lambda _driver: self.driver.execute_script(
                    "return document.readyState") == "complete"
            )
            time.sleep(self.loading_delay)
            logging.info(f"等待{self.loading_delay}秒页面加载完成...")
            self.find_button()
        except TimeoutException:
            logging.error("页面元素加载超时")
            self.driver.quit()
            return
    def find_button(self):
        try:
            # 查找按钮
            button = WebDriverWait(self.driver, 10).until(
                lambda _driver: self.driver.find_element(
                    By.XPATH, '//button[text()="Where am i?"]')
            )
            button.click()
            logging.info("点击按钮")
            # 定位具有特定 placeholder 的输入框
            self.input_box = WebDriverWait(self.driver, 10).until(
                lambda _driver: self.driver.find_element(
                    By.XPATH, '//input[@placeholder="Paste file name here"]')
            )
        except TimeoutException:
            logging.error("页面元素加载超时")
            self.driver.quit()
            return
        

def main(browser: str, game_map: str):
    loading_delay = config.getint("DEFAULT", "LoadingDelay", fallback=5)
    driver = None
    if browser == 'firefox':
        driver = webdriver.Firefox(
            service=FirefoxService(GeckoDriverManager().install()))
    elif browser == 'chrome':
        driver = webdriver.Chrome(service=ChromeService(
            ChromeDriverManager().install()))
    else:
        raise ValueError("不支持的浏览器")
    path = config.get("DEFAULT", "ScreenShotPath", fallback=None)
    if path is None or path == "":
        raise ValueError("截图路径未设置")
    logging.info(f"截图路径设定为: {path}")
    event_handler = MyHandler(driver,loading_delay)
    observer = Observer()
    observer.schedule(event_handler, path, recursive=False)
    driver.get(f'https://tarkov-market.com/maps/{game_map}')
    event_handler.page_init()
    logging.info("准备完毕，开始监听截图文件夹...")
    observer.start()

    while True:
        try:
            # 检测窗口是否关闭
            _handle = driver.current_window_handle
            time.sleep(1)
        except NoSuchWindowException:
            logging.info("浏览器窗口关闭，程序结束")
            observer.stop()
            observer.join(timeout=1)
            driver.quit()
            logging.info("程序结束")
            break


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='ESTGPS', description='Automatics coordinate parser for EFT')
    parser.add_argument('-b', '--browser',
                        choices=['firefox', 'chrome'], default='chrome')
    parser.add_argument('-m', '--map', default="ground-zero")
    args = parser.parse_args()
    try:
        main(args.browser, args.map)
    except KeyboardInterrupt:
        print("程序结束")
    except Exception as e:
        logging.error(e)
        print("程序异常结束")
