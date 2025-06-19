from Shipment.IShipment import IShipmentScraper
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from Helpers.retryable import retryable
from Helpers.logging_config import setup_logger
from selenium.webdriver.remote.webelement import WebElement
import time

log = setup_logger()

TIMEOUT = 60
CONTAINER_TABLE_ID = "//*[@id='main-grid']/tbody"
CONTAINER_ROW_XPATH = "./tr[@id]"
NUMBER_OF_CONTAINER_RESULTS_ID = "totCnt"


class OneShipmentScraper(IShipmentScraper):
    _page: WebDriver
    def __init__(self, page):
        self._page = page

    @retryable(max_retries=5, delay=5, exceptions=(NoSuchElementException, ValueError))
    def _get_total_number_of_container_results(self) -> int:
        time.sleep(5) # wait for the total count in dom to update, default is 0, and takes time to load
        containers_count = self._page.find_element(
            By.ID, NUMBER_OF_CONTAINER_RESULTS_ID
        ).text.strip()
        return int(containers_count)

    @retryable(max_retries=3, delay=2, exceptions=(TimeoutException,))
    def get_container_elements(self) -> list[WebElement]:
        if self._get_total_number_of_container_results() < 1:
            log.warning("No container/s found in shipment.")
            return []

        container_table = WebDriverWait(self._page, TIMEOUT).until(
            EC.visibility_of_element_located((By.XPATH, CONTAINER_TABLE_ID))
        )

        container_elements = WebDriverWait(container_table, TIMEOUT).until(
            EC.visibility_of_all_elements_located((By.XPATH, CONTAINER_ROW_XPATH))
        )

        return container_elements
