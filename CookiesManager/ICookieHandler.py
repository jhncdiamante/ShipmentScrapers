from abc import ABC, abstractmethod


class ICookieHandler(ABC):
    @abstractmethod
    def allow_cookies_permission(self):
        pass
