from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
import logging


def is_captcha_page(driver, timeout: int = 3) -> bool:
    """
    Проверяет наличие CAPTCHA на странице.

    :param driver: Экземпляр WebDriver.
    :param timeout: Таймаут ожидания поиска элементов CAPTCHA.
    :return: True если CAPTCHA обнаружена, иначе False.
    """
    captcha_selectors = [
        "//form[@id='captcha-form']",
        "//div[@id='recaptcha']",
        "//iframe[contains(@src, 'recaptcha/api2/anchor')]",
        "//p[contains(text(), 'подозрительный трафик')]"
    ]
    original_timeout = driver.timeouts.implicit_wait
    driver.implicitly_wait(timeout)
    try:
        for selector in captcha_selectors:
            if driver.find_elements(By.XPATH, selector):
                logging.warning(f"CAPTCHA обнаружена по селектору: {selector}")
                return True
        if "google.com/sorry/" in driver.current_url or "введите символы" in driver.page_source:
            logging.warning("CAPTCHA обнаружена по URL или тексту.")
            return True
    finally:
        driver.implicitly_wait(original_timeout)
    return False


def handle_cookie_consent(driver, timeout: int = 5) -> bool:
    """
    Обрабатывает всплывающее окно согласия на cookies.

    :param driver: Экземпляр WebDriver.
    :param timeout: Таймаут ожидания появления кнопки.
    :return: True, если клик выполнен, иначе False.
    """
    selectors = [
        "//button[@id='L2AGLb']",
        "//div[text()='Принять все']/ancestor::button[1]",
        "//button[.//span[contains(text(), 'Принять все') or contains(text(), 'Accept all')]]",
        "//button[.//div[contains(text(), 'Принять все') or contains(text(), 'Accept all')]]",
        "//div[@role='dialog']//button[contains(., 'Accept all') or contains(., 'Принять все')][last()]"
    ]
    for i, selector in enumerate(selectors):
        try:
            button = WebDriverWait(driver, timeout + i).until(
                EC.element_to_be_clickable((By.XPATH, selector))
            )
            driver.execute_script("arguments[0].scrollIntoView(true);", button)
            time.sleep(0.5)
            button.click()
            logging.info(f"Принято cookie по селектору: {selector}")
            return True
        except TimeoutException:
            continue
    return False
