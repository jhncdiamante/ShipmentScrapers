from abc import ABC, abstractmethod

class IShipmentScraper(ABC):
    @abstractmethod
    def get_container_elements(self, shipment_id):
        pass

    




