from Search.SearchBar import SearchBar
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC 
from selenium.webdriver.common.keys import Keys
from Helpers.retryable import retryable
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from Helpers.logging_config import setup_logger

logging = setup_logger()
SEARCH_BAR_ID = "mc-input-track-input"

class MaerskSearchBar(SearchBar):

    @retryable(max_retries=3, delay=2, exceptions=(TimeoutException, NoSuchElementException,))
    def type(self, keyword: str):
        # Wait for the shadow host element
        host = WebDriverWait(self._driver, 30).until(
            EC.visibility_of_element_located(self.locator)
        )
        # Access shadow DOM
        shadow_root = self._driver.execute_script("return arguments[0].shadowRoot", host)
        # Find the input inside the shadow DOM
        bar = shadow_root.find_element(By.ID, SEARCH_BAR_ID)
        # Send the keyword
        bar.send_keys(Keys.CONTROL + "a", Keys.BACKSPACE)
        bar.send_keys(keyword)
        logging.info(f"Successfully typed booking number in search bar...")
