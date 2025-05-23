from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium_stealth import stealth
from webdriver_manager.chrome import ChromeDriverManager
import random
import time
from typing import Optional

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:102.0) Gecko/20100101 Firefox/102.0",
    # Добавьте больше user-agent по желанию
]

def create_stealth_driver(headless: bool = False, proxy: Optional[str] = None) -> webdriver.Chrome:
    """
    Создает Chrome WebDriver с маскировкой selenium-stealth.

    :param headless: Запускать браузер в headless-режиме.
    :param proxy: Адрес прокси (например, 'http://127.0.0.1:8080'), если нужен.
    :return: Объект Chrome WebDriver.
    """
    options = webdriver.ChromeOptions()
    if headless:
        options.add_argument("--headless=new")  # Используем новый headless Chrome
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--lang=ru-RU,ru;q=0.9")

    if proxy:
        options.add_argument(f'--proxy-server={proxy}')

    user_agent = random.choice(USER_AGENTS)
    options.add_argument(f'user-agent={user_agent}')

    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    stealth(driver,
            languages=["ru-RU", "ru"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True,
    )

    return driver


def simulate_user_activity(driver: webdriver.Chrome) -> None:
    """
    Симулирует поведение пользователя на странице:
    - случайные движения мыши,
    - прокрутка страницы.

    :param driver: Объект WebDriver.
    :return: None
    """
    # Прокрутка вниз-вверх с паузами
    for _ in range(random.randint(2, 5)):
        scroll_height = driver.execute_script("return document.body.scrollHeight")
        position = random.randint(0, scroll_height)
        driver.execute_script(f"window.scrollTo(0, {position});")
        time.sleep(random.uniform(0.5, 1.5))

    # Можно добавить перемещения мыши через ActionChains, но не всегда нужно



