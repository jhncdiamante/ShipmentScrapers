from abc import ABC, abstractmethod


class IContainerScraper(ABC):

    @abstractmethod
    def get_id(self):
        pass

    @abstractmethod
    def get_status(self):
        pass

    @abstractmethod
    def get_milestone_elements(self):
        pass

    @abstractmethod
    def get_estimated_time_arrival(self):
        pass
