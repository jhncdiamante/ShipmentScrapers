import logging
from abc import ABC, abstractmethod

class IContainerScraper(ABC):
    logger = logging.getLogger("container.scraper")

    def get_id(self):
        self.logger.info(f"{self.__class__.__name__} - Getting container ID")
        return self._get_id()  # Call the subclass's version

    def get_status(self):
        self.logger.info(f"{self.__class__.__name__} - Getting container status")
        return self._get_status()

    def get_milestone_elements(self):
        self.logger.info(f"{self.__class__.__name__} - Getting milestone elements")
        return self._get_milestone_elements()

    def get_estimated_time_arrival(self):
        self.logger.info(f"{self.__class__.__name__} - Getting ETA")
        return self._get_estimated_time_arrival()

    @abstractmethod
    def _get_id(self): pass

    @abstractmethod
    def _get_status(self): pass

    @abstractmethod
    def _get_milestone_elements(self): pass

    @abstractmethod
    def _get_estimated_time_arrival(self): pass
