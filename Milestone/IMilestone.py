from abc import ABC, abstractmethod


class IMilestoneScraper(ABC):

    @abstractmethod
    def get_date(self):
        pass

    @abstractmethod
    def get_event(self):
        pass

    @abstractmethod
    def get_vessel(self):
        pass

    @abstractmethod
    def get_location(self):
        pass
