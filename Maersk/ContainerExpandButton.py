from Button.Button import Button
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from Helpers.retryable import retryable
from selenium.common.exceptions import (
    TimeoutException,
)
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.remote.webdriver import WebDriver


EXCEPTIONS = (TimeoutException,)
TIMEOUT = 15


class MaerskContainerExpandButton(Button):
    # Extended class for button specifically for Maersk Website
    def __init__(self, locator: tuple, element: WebElement, driver: WebDriver):
        super().__init__(locator, driver)
        self._element = element

    def click(self):
        button_element = self._get_button_element()
        self._driver.execute_script(
            """
                arguments[0].scrollIntoView({ 
                    behavior: 'smooth', 
                    block: 'center', 
                    inline: 'center' 
                });
            """,
            button_element,
        )
        button_element.click()

    @retryable(max_retries=3, delay=2, exceptions=EXCEPTIONS)
    def get_state(self) -> bool:
        # Checks the attribute of button element that states the button's current state (closed, expanded)
        button = self._get_button_element()
        return button.get_attribute("aria-expanded") == "true"

    @retryable(max_retries=3, delay=2, exceptions=EXCEPTIONS)
    def get_panel_reference(self) -> str:
        # returns the ID ref of an element that expands if the said button is clicked
        button = self._get_button_element()
        return button.get_attribute("aria-controls")

    @retryable(max_retries=3, delay=2, exceptions=EXCEPTIONS)
    def _get_button_element(self) -> WebElement:
        # returns the ID ref of an element that expands if the said button is clicked
        return WebDriverWait(self._element, TIMEOUT).until(
            EC.element_to_be_clickable(self._locator)
        )
