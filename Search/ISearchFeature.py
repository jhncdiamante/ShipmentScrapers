from abc import ABC, abstractmethod


class ISearchFeature(ABC):

    @abstractmethod
    def search(self):
        pass
