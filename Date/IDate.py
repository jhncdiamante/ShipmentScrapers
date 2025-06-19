from abc import ABC, abstractmethod


class IDate(ABC):
    @abstractmethod
    def get_current_time(self):
        pass
