from Button.IButton import IButton
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webdriver import WebDriver
from Helpers.retryable import retryable
from selenium.common.exceptions import (
    TimeoutException,
    ElementClickInterceptedException,
    ElementNotInteractableException,
)
from selenium.webdriver.remote.webdriver import WebDriver

TIMEOUT = 15
EXCEPTIONS = (
    TimeoutException,
    ElementClickInterceptedException,
    ElementNotInteractableException
)


class Button(IButton):
    def __init__(self, locator, driver):
        self._driver: WebDriver = driver
        self._locator: tuple = locator

    @retryable(max_retries=5, delay=2, exceptions=EXCEPTIONS)
    def click(self) -> None:
        button_element = WebDriverWait(self._driver, TIMEOUT).until(
            EC.element_to_be_clickable(self._locator)
        ) # locate the button using locator
        # scroll to the button
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
        self._driver.execute_script("arguments[0].click();", button_element) # click button
