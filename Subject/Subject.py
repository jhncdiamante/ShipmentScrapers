# observer_pattern.py
from abc import ABC, abstractmethod

class Observer(ABC):
    @abstractmethod
    def update(self, data: dict):
        pass

class Subject(ABC):
    def __init__(self):
        self._observers: list[Observer] = []
        

    def attach(self, observer: Observer):
        self._observers.append(observer)

    def detach(self, observer: Observer):
        self._observers.remove(observer)

    def notify(self):
        print("Notifying...")
        for observer in self._observers:
            observer.update(self.current_data)
