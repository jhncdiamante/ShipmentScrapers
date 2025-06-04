from abc import abstractmethod, ABC

class IDatabase(ABC):
    @abstractmethod
    def update(self):
        pass