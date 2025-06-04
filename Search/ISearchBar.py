from abc import ABC, abstractmethod

class ISearchBar(ABC):

    @abstractmethod
    def type(self, keyword: str):
        pass
