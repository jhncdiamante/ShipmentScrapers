from abc import ABC, abstractmethod


class IWebsite(ABC):
    @abstractmethod
    def open(self):
        pass

    @abstractmethod
    def close(self):
        pass
