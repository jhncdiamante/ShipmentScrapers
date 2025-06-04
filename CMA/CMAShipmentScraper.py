from Shipment.IShipment import IShipmentScraper

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from Helpers.retryable import retryable
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.remote.webdriver import WebDriver
TIMEOUT = 30


CONTAINER_CLASS_NAME = "cardelem"
SINGLE_CONTAINER_ID = "trackingsearchsection"

class CMAShipmentScraper(IShipmentScraper):
    def __init__(self, page: WebDriver):
        self.page = page

    @retryable(max_retries=3, delay=2, exceptions=(TimeoutException,))
    def get_container_elements(self) -> list[WebElement]:
        # When a shipment has only one present container in the website, the website structure is different as opposed
        # to the ones with multiple containers
        try:
            containers = WebDriverWait(self.page, TIMEOUT).until(
                EC.visibility_of_all_elements_located((By.CLASS_NAME, CONTAINER_CLASS_NAME))
            )
            return containers
            
        except TimeoutException as e:
            
            single_container = WebDriverWait(self.page, TIMEOUT).until(
                EC.visibility_of_element_located((By.ID, SINGLE_CONTAINER_ID))
            )
            return [single_container]