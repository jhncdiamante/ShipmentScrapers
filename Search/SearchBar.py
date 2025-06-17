from Search.ISearchBar import ISearchBar
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from Helpers.logging_config import setup_logger
from selenium.webdriver.remote.webelement import WebElement

log = setup_logger()

class SearchBar(ISearchBar):
    def __init__(self, driver, locator: tuple):
        self._driver = driver
        self.locator = locator

    def type(self, keyword: str):
        search_bar = WebDriverWait(self._driver, 60).until(
            EC.element_to_be_clickable(self.locator)
        )
        if self._has_content(search_bar):
            log.info("Clearing previous keyword..")
            search_bar.clear()
        search_bar.send_keys(keyword)

    def _has_content(self, search_bar: WebElement) -> bool:
        return search_bar.get_attribute("value").strip()