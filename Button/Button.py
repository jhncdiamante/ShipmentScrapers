from Button.IButton import IButton
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webdriver import WebDriver
from Helpers.retryable import retryable
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.remote.webelement import WebElement

class Button(IButton):
    def __init__(self, locator: tuple, element: WebElement, driver=None):
        self._driver = driver
        self._element = element
        self._locator = locator

    @retryable(max_retries=3, delay=2, exceptions=(TimeoutException,))
    def click(self, head=False):
        button_element = WebDriverWait(self._element, 30).until(EC.element_to_be_clickable(self._locator))
        if head and isinstance(self._driver, WebDriver):
            self._driver.execute_script("""
                arguments[0].scrollIntoView({ 
                    behavior: 'smooth', 
                    block: 'center', 
                    inline: 'center' 
                });
            """, button_element)
        self._driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", button_element)
        button_element.click()



