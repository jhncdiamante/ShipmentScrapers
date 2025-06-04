from Search.ISearchBar import ISearchBar
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class SearchBar(ISearchBar):
    def __init__(self, driver, locator: tuple):
        self._driver = driver
        self.locator = locator

    def type(self, keyword: str):
        element = WebDriverWait(self._driver, 30).until(
            EC.element_to_be_clickable(self.locator)
        )
        element.clear() 
        element.send_keys(keyword)
