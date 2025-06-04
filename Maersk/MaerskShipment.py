from Shipment.IShipment import IShipmentScraper
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from Helpers.logging_config import setup_logger

logging = setup_logger()

CONTAINER_FRAME_CLASS_NAME = "track-grid__content"
CONTAINER_CSS_SELECTOR = 'div[data-test="container"]'

class MaerskShipmentScraper(IShipmentScraper):
    def __init__(
        self,
        page_handle: WebDriver
    ):
        self._page_handle = page_handle

    def get_container_elements(self):
        c_elements = WebDriverWait(self._page_handle, 30).until(
            EC.visibility_of_all_elements_located((By.CSS_SELECTOR, CONTAINER_CSS_SELECTOR))
        )
        logging.info(f"Reading {len(c_elements)} container elements...")
        return c_elements
     