from Search.ISearchBar import ISearchBar
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from Helpers.logging_config import setup_logger
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.remote.webdriver import WebDriver
from Helpers.retryable import retryable
from selenium.common.exceptions import ElementClickInterceptedException
log = setup_logger()


class SearchBar(ISearchBar):
    _driver: WebDriver
    _locator: tuple
    def __init__(self, driver, locator):
        self._driver = driver
        self._locator = locator

    @retryable(max_retries=3, delay=3, exceptions=(ValueError, ElementClickInterceptedException))
    def type(self, keyword: str) -> None:
        search_bar = WebDriverWait(self._driver, 60).until(
            EC.element_to_be_clickable(self._locator)
        )
        
        if self._has_content(search_bar):
            log.info("Clearing previous keyword with JS..")
            self._driver.execute_script("arguments[0].value = '';", search_bar)

        log.info(f"Typing keyword '{keyword}' with JS..")
        self._driver.execute_script("arguments[0].value = arguments[1];", search_bar, keyword)

        # sometimes JS-set value doesn’t trigger input events, so force it
        self._driver.execute_script(
            "arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", 
            search_bar
        )

    def _has_content(self, search_bar: WebElement) -> bool:
        return search_bar.get_attribute("value").strip() != ""
