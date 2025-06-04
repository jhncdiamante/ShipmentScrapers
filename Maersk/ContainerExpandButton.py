
from Button.Button import Button
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from Helpers.retryable import retryable
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException, ElementNotInteractableException


class MaerskContainerExpandButton(Button):
    # Extended class for button specifically for Maersk Website

    @retryable(max_retries=3, delay=2, exceptions=(TimeoutException, NoSuchElementException, ElementNotInteractableException, ElementClickInterceptedException,))
    def get_state(self) -> bool:
        # Checks the attribute of button element that states the button's current state (closed, expanded)
        button = WebDriverWait(self._element, 30).until(EC.element_to_be_clickable(self._locator))
        return button.get_attribute("aria-expanded") == "true"
    
    @retryable(max_retries=3, delay=2, exceptions=(TimeoutException, NoSuchElementException, ElementNotInteractableException, ElementClickInterceptedException,))
    def get_panel_reference(self) -> str:
        # returns the ID ref of an element that expands if the said button is clicked
        button = WebDriverWait(self._element, 30).until(EC.element_to_be_clickable(self._locator))
        return button.get_attribute('aria-controls')
