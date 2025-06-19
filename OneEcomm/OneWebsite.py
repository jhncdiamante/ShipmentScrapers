from Website.TrackingWebsite import TrackingWebsite
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from Helpers.retryable import retryable
from selenium.common.exceptions import TimeoutException

TIMEOUT = 30
IFRAME_ID = "IframeCurrentEcom"


class OneWebsite(TrackingWebsite):

    def open(self):
        super().open()
        self._go_to_main_page()

    @retryable(max_retries=3, delay=2, exceptions=(TimeoutException,))
    def _go_to_main_page(self):
        iframe = WebDriverWait(self._driver, TIMEOUT).until(
            EC.visibility_of_element_located((By.ID, IFRAME_ID))
        )
        self._driver.switch_to.frame(iframe)
