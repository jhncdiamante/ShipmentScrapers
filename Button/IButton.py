
from abc import ABC, abstractmethod

class IButton(ABC):
    @abstractmethod
    def click(self, head):
        pass

    