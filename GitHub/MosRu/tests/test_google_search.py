import pytest
from browser_setup import create_stealth_driver, simulate_user_activity
from selenium.webdriver.common.by import By

def is_captcha_page(driver) -> bool:
    """
    Проверяет, отображается ли страница с CAPTCHA Google.

    :param driver: WebDriver.
    :return: True, если CAPTCHA найдена, иначе False.
    """
    try:
        driver.find_element(By.XPATH, "//form[@id='captcha-form']")
        return True
    except:
        return False

@pytest.fixture(scope="session")
def driver():
    driver_instance = create_stealth_driver(headless=False)
    yield driver_instance
    driver_instance.quit()

def test_google_search_mosru_hit(driver):
    search_query = "mos.ru"
    expected_phrase = "Услуга-хит"
    search_url = f"https://www.google.com/search?q={search_query}&hl=ru&gl=ru&lr=lang_ru"

    driver.get(search_url)
    simulate_user_activity(driver)

    if is_captcha_page(driver):
        with open("google_captcha_page.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        pytest.fail("CAPTCHA обнаружена. HTML сохранен.")

    assert expected_phrase in driver.page_source, f"Фраза '{expected_phrase}' не найдена на странице"
