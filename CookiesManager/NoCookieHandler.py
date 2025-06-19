from CookiesManager.ICookieHandler import ICookieHandler


class NoCookieHandler(ICookieHandler):
    def allow_cookies_permission(self) -> None:
        # do nothing >_<
        pass
