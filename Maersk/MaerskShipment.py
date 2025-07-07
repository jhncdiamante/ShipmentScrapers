from Shipment.IShipment import IShipmentScraper
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import TimeoutException
from Helpers.retryable import retryable
from Helpers.logging_config import setup_logger

logging = setup_logger()

CONTAINER_CSS_SELECTOR = 'div[data-test="container"]'
TIMEOUT = 15


class MaerskShipmentScraper(IShipmentScraper):
    _page_handle: WebDriver
    def __init__(self, page_handle):
        self._page_handle = page_handle
    
    @retryable(max_retries=5, delay=2, exceptions=(TimeoutException,))
    def get_container_elements(self) -> list[WebElement]:
        try:
            c_elements = WebDriverWait(self._page_handle, TIMEOUT).until(
                EC.visibility_of_all_elements_located(
                    (By.CSS_SELECTOR, CONTAINER_CSS_SELECTOR)
                )
            )
            return c_elements
        except TimeoutException:
            self._page_handle.refresh()
            raise TimeoutException
