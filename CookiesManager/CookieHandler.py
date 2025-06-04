from Button.IButton import IButton
from CookiesManager.ICookieHandler import ICookieHandler

class CookieHandler(ICookieHandler):
    def __init__(self, driver, allow_cookies_button: IButton):
        self._driver = driver
        self._allow_cookies_button = allow_cookies_button

    def allow_cookies_permission(self):
        try:
            self._allow_cookies_button.click()
        except Exception:
            print(f"Cookies Button wasn't clicked because it was not present or could not be located.")
            pass
    