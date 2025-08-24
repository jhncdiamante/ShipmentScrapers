from Website.IWebsite import IWebsite
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.remote.webdriver import WebDriver
from Search.ISearchFeature import ISearchFeature
from CookiesManager.ICookieHandler import ICookieHandler
from typing import Callable
from selenium.webdriver.remote.webelement import WebElement
from Container.IContainer import IContainerScraper
from Milestone.IMilestone import IMilestoneScraper
from Shipment.IShipment import IShipmentScraper
from Shipment.IShipment import IShipmentScraper
from Helpers.logging_config import setup_logger
from Helpers.Screenshot import screenshot

logger = setup_logger()
STANDARD_EVENTS = {"Gate in", "Departure", "Arrival", "Discharge", "Gate out"}


class TrackingWebsite(IWebsite):
    def __init__(
        self,
        url,
        driver,
        search_feature,
        cookie_handler,
        shipment_scraper,
        container_scraper,
        milestone_scraper,
        scrape_time,
        name
    ):
        self.url = url
        self._driver: WebDriver = driver
        self._search_feature: ISearchFeature = search_feature
        self._cookie_handler: ICookieHandler = cookie_handler

        self._shipment_scraper: Callable[[WebDriver], IShipmentScraper] = shipment_scraper
        self._container_scraper: Callable[[WebElement, WebDriver], IContainerScraper] = container_scraper
        self._milestone_scraper: Callable[[WebElement], IMilestoneScraper] = milestone_scraper
        self._scrape_time = scrape_time
        self.name = name


    def __str__(self):
        return self.name

    def open(self) -> None:
        self._driver.get(self.url)
        WebDriverWait(self._driver, 30).until(
            lambda _: self._driver.execute_script("return document.readyState")
            == "complete"
        )
        self._cookie_handler.allow_cookies_permission()

    def close(self) -> None:
        self._driver.quit()

    def _search_by_bill_of_lading(self, shipment_id) -> None:
        self._search_feature.search(shipment_id)

    def track_shipment(self, shipment_id: int) -> dict:
        self._search_by_bill_of_lading(shipment_id)
        shipment = self._shipment_scraper(self._driver)
        containers = shipment.get_container_elements()
        self._driver.execute_script("document.body.style.zoom = '0.5'")

        shipment_data = {
            "bill_of_lading_number": shipment_id,
            "containers": [self._process_container(c, shipment_id) for c in containers]
        }
        import json
        with open(f"{shipment_id}.json", "w", encoding="utf-8") as f:
            json.dump(shipment_data, f, ensure_ascii=False, indent=4)


        containers_data = []

        for container in shipment_data.get("containers"):
            milestones = container.get("milestones")
            destination = container.get("destination").lower()
            origin = container.get("origin").lower()

            dynamic_milestones = {"Departure": [],
                                  "Arrival": []}

            milestones_data = {
                "Gate in": None,
                "Departure": None,
                "Departure Vessel Name": None,
                "Departure Voyage ID": None,
                "Departure Location": None,
                "Arrival": None,
                "Arrival Vessel Name": None,
                "Arrival Voyage ID": None,
                "Arrival Location": None,
                "Discharge": None,
                "Gate out": None,
            }
            for milestone in milestones:
                m_loc = milestone.get("location").lower()
                m_event = milestone.get("event")

                if m_event not in STANDARD_EVENTS:
                    continue

                m_date = milestone.get("date")
                m_voyage_id = milestone.get("voyage_id")
                m_voyage_name = milestone.get("voyage_name")

                if m_event in {"Departure", "Arrival"}:
                    dynamic_milestones[m_event].append(f"{milestone.get("location")}")

                if (
                    milestones_data[m_event] is not None
                    and m_event not in {"Gate in", "Departure"}
                ) or (milestones_data[m_event] is None):
                    
                    if m_event in {"Departure", "Arrival"}:
                        if (m_loc in origin and m_event == "Departure") or (m_loc in destination and m_event == "Arrival"):
                            milestones_data[f"{m_event} Vessel Name"] = m_voyage_name 
                            milestones_data[f"{m_event} Voyage ID"] = m_voyage_id
                            milestones_data[f"{m_event} Location"] = milestone.get("location")
                        else:
                            continue
                    elif m_event in {"Discharge", "Gate out"}:
                        if not m_loc in destination:
                            continue

                    milestones_data[m_event] = m_date

                arrivals = [m.get("date") for m in milestones if m.get("event") == "Arrival"]
                estimated_time_arrival = (
                    milestones_data.get("Arrival")
                    or (arrivals[-1] if arrivals else "")
                )
                current_time = self._scrape_time.get_current_time()

                
            containers_data.append({
                "Scrape Time": current_time,
                "Shipment ID": shipment_id,
                "Origin": container.get("origin"),
                "Destination": container.get("destination"),
                "Container ID": container.get("identifier"),
                "Status": container.get("status"),
                "ETA": estimated_time_arrival,
            } | milestones_data | 
            {
                "Arrival Entries": "; ".join(dynamic_milestones["Arrival"]),
                "Departure Entries": "; ".join(dynamic_milestones["Departure"]),

            })

        return containers_data


    def _process_container(self, container_element: WebElement, bl_number: str) -> dict:
        container = self._container_scraper(container_element, self._driver)
        container_id = container.get_id()
        container_data = {
            "identifier": container_id,
            "status": container.get_status(),
            "milestones": self._process_milestones(container),
            "origin": container.get_origin(),
            "destination": container.get_destination(),
        }

        screenshot(self._driver, str(self), bl_number=bl_number, container_number=container_id)

        return container_data


    def _process_milestones(self, container) -> list:
        milestones = container.get_milestone_elements()
        milestones_data = []
        for milestone in milestones:
            milestone = self._milestone_scraper(milestone)
            event = milestone.get_event()
            voyage_id, voyage_name = milestone.get_vessel()
            milestone_location = milestone.get_location()
            milestone_date = milestone.get_date()

            milestones_data.append({
                "event": event,
                "date": milestone_date,
                "voyage_id": voyage_id,
                "voyage_name": voyage_name,
                "location": milestone_location,
            })
        return milestones_data
    