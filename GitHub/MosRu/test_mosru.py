import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import logging
import time

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

@pytest.fixture(scope="session")
def driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--lang=ru-RU,ru;q=0.9")
    options.add_experimental_option('prefs', {'intl.accept_languages': 'ru-RU,ru'})
    # Попытка выдать себя за обычный браузер
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36')
    options.add_experimental_option("excludeSwitches", ["enable-automation"]) # Попытка скрыть флаг автоматизации
    options.add_experimental_option('useAutomationExtension', False)


    driver_instance = None
    try:
        logging.info("Инициализация WebDriver Chrome в headless-режиме.")
        driver_instance = webdriver.Chrome(options=options)
        yield driver_instance
    finally:
        if driver_instance:
            driver_instance.quit()
            logging.info("WebDriver закрыт.")

def is_captcha_page(driver_instance, timeout=3):
    """Проверяет, загружена ли страница CAPTCHA."""
    captcha_selectors = [
        "//form[@id='captcha-form']",
        "//div[@id='recaptcha']",
        "//iframe[contains(@src, 'recaptcha/api2/anchor')]",
        "//p[contains(text(), 'подозрительный трафик')]" # Проверка по тексту
    ]
    original_implicit_wait = driver_instance.timeouts.implicit_wait
    driver_instance.implicitly_wait(timeout) # Устанавливаем короткое неявное ожидание для быстрой проверки
    try:
        for selector in captcha_selectors:
            if driver_instance.find_elements(By.XPATH, selector):
                logging.warning(f"Обнаружена страница CAPTCHA по селектору: {selector}")
                return True
        # Дополнительная проверка по заголовку или URL, если предыдущие не сработали
        if "google.com/sorry/" in driver_instance.current_url or "Чтобы продолжить, введите символы" in driver_instance.page_source:
             logging.warning("Обнаружена страница CAPTCHA по URL или тексту.")
             return True
    except Exception: # Любая ошибка при поиске означает, что элемента, скорее всего, нет
        pass
    finally:
        driver_instance.implicitly_wait(original_implicit_wait) # Возвращаем исходное значение
    return False

def handle_cookie_consent(driver_instance, timeout=5):
    possible_consent_selectors = [
        "//button[@id='L2AGLb']",
        "//div[text()='Принять все']/ancestor::button[1]",
        "//button[.//span[contains(text(), 'Принять все') or contains(text(), 'Accept all')]]",
        "//button[.//div[contains(text(), 'Принять все') or contains(text(), 'Accept all')]]",
        "//div[@role='dialog']//button[contains(., 'Accept all') or contains(., 'Принять все')][last()]"
    ]
    for i, selector in enumerate(possible_consent_selectors):
        try:
            # Используем явное ожидание для кнопки согласия
            consent_button = WebDriverWait(driver_instance, timeout if i < len(possible_consent_selectors) -1 else timeout + 2).until(
                EC.element_to_be_clickable((By.XPATH, selector))
            )
            driver_instance.execute_script("arguments[0].scrollIntoView(true);", consent_button)
            time.sleep(0.5)
            consent_button.click()
            logging.info(f"Диалог о cookie обработан с помощью селектора: {selector}")
            time.sleep(1) # Даем время диалогу исчезнуть
            return True
        except TimeoutException:
            logging.debug(f"Селектор для cookie {selector} не найден или кнопка не кликабельна.")
            continue
    logging.info("Диалог о cookie не найден или не удалось обработать доступными селекторами.")
    return False

def test_Google_Search_mosru_usluga_hit(driver):
    search_query = "mos.ru"
    expected_phrase = "Услуга-хит"
    search_url = f"https://www.google.com/search?q={search_query}&hl=ru&gl=ru&lr=lang_ru"

    logging.info(f"Открываем страницу: {search_url}")
    driver.get(search_url)

    # Первым делом проверяем на CAPTCHA
    if is_captcha_page(driver):
        page_source_path = "google_captcha_page.html"
        try:
            with open(page_source_path, "w", encoding="utf-8") as f:
                f.write(driver.page_source)
            logging.error(f"Обнаружена страница CAPTCHA. Тест не может быть продолжен. HTML сохранен в {page_source_path}")
        except Exception as e_save:
            logging.error(f"Не удалось сохранить HTML страницы CAPTCHA: {e_save}")
        pytest.fail(f"Обнаружена страница CAPTCHA от Google. Проверьте настройки сети/IP или частоту запросов. HTML сохранен в {page_source_path}")
        return # На всякий случай, хотя pytest.fail должен прервать выполнение

    logging.info("Страница CAPTCHA не обнаружена. Пытаемся обработать диалог о cookie.")
    handle_cookie_consent(driver)

    first_result_description_selector = \
        "(//div[.//h3[parent::a]])[1]//div[count(.//a)=0 and count(.//cite)=0 and count(.//h3)=0 and string-length(normalize-space(.)) > 10][1]"

    logging.info(f"Ожидаем загрузки результатов поиска и ищем описание первого результата по XPath: {first_result_description_selector}")
    try:
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, "//div[.//h3[parent::a]]")) # Ожидание любого результата
        )
        logging.info("Контейнер с результатами поиска найден.")

        first_result_description_element = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, first_result_description_selector))
        )
        description_text = first_result_description_element.text
        logging.info(f"Текст описания первого результата: '{description_text}'")

        assert expected_phrase in description_text, \
            f"Фраза '{expected_phrase}' НЕ найдена в описании первого результата. Найдено: '{description_text}'"
        logging.info(f"УСПЕХ: Фраза '{expected_phrase}' найдена в описании первого результата.")

    except TimeoutException:
        page_source_path = "Google Search_page_on_timeout.html"
        try:
            with open(page_source_path, "w", encoding="utf-8") as f:
                f.write(driver.page_source)
            logging.error(f"Timeout: Не удалось дождаться или найти описание первого результата. HTML сохранен в {page_source_path}")
        except Exception as e_save:
            logging.error(f"Не удалось сохранить HTML страницы: {e_save}")
        pytest.fail(f"Timeout: Не удалось дождаться или найти описание первого результата поиска. Проверьте селектор XPath и доступность элемента. HTML сохранен в {page_source_path}")
    except Exception as e:
        page_source_path = "Google Search_page_on_general_exception.html"
        logging.error(f"Произошла непредвиденная ошибка: {e}", exc_info=True)
        try:
            with open(page_source_path, "w", encoding="utf-8") as f:
                f.write(driver.page_source)
            logging.info(f"HTML страницы при ошибке сохранен в {page_source_path}")
        except Exception as e_save:
            logging.error(f"Не удалось сохранить HTML страницы при ошибке: {e_save}")
        pytest.fail(f"Произошла непредвиденная ошибка: {e}")