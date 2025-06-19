from Button.IButton import IButton
from CookiesManager.ICookieHandler import ICookieHandler
from Helpers.logging_config import setup_logger
from selenium.webdriver.remote.webdriver import WebDriver

log = setup_logger()


class CookieHandler(ICookieHandler):
    _driver: WebDriver
    _allow_cookies_button: IButton
    def __init__(self, driver, allow_cookies_button):
        self._driver = driver
        self._allow_cookies_button = allow_cookies_button

    def allow_cookies_permission(self) -> None:
        try:
            self._allow_cookies_button.click()
        except Exception as e:
            log.warning(
                f"Cookies Button wasn't clicked because it was not present or could not be located: {e}"
            )
