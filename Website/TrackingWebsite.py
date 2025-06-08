
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
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
from Subject.Subject import Subject
from Date.IDate import IDate
import time, random
from Helpers.logging_config import setup_logger

logger = setup_logger()
STANDARD_EVENTS = {"Gate in", "Departure", "Arrival", "Discharge", "Gate out"}
OPTIONAL_EVENTS = ["Arrival", "Discharge", "Gate out"]



class TrackingWebsite(Subject, IWebsite):
    def __init__(self, url, driver, search_feature, cookie_handler,
        shipment_scraper_factory: Callable[[WebDriver], IShipmentScraper],
        container_scraper_factory: Callable[[WebElement, WebDriver], IContainerScraper],
        milestone_scraper_factory: Callable[[WebElement], IMilestoneScraper],
        scrape_time: Callable[[], IDate]):
        super().__init__()
        self.url = url
        self._driver: WebDriver = driver
        self._search_feature: ISearchFeature = search_feature
        self._cookie_handler: ICookieHandler = cookie_handler

        self._shipment_scraper = shipment_scraper_factory
        self._container_scraper = container_scraper_factory
        self._milestone_scraper = milestone_scraper_factory
        self._scrape_time = scrape_time
        self._current_data = None

    @property
    def current_data(self):
        return self._current_data


    @current_data.setter
    def current_data(self, current_data):
        self._current_data = current_data
        self.notify()

    def open(self):
        self._driver.get(self.url)
        WebDriverWait(self._driver, 30).until(
            lambda _: self._driver.execute_script('return document.readyState') == 'complete'
        )
        self._cookie_handler.allow_cookies_permission()

    def close(self):
        self._driver.close()

    def track_shipment(self, shipment_id):
        logger.info(f"Searching {shipment_id}...")
        self._search_feature.search(shipment_id)
        logger.info(f"Successfully searched {shipment_id}.")
        logger.info("Initializing shipment scraper...")
        shipment_scraper = self._shipment_scraper(self._driver)
        logger.info("Extracting container elements...")
        container_elements = shipment_scraper.get_container_elements()
        logger.info(f"Successfully read {len(container_elements)} containers.")

        for idx, cont_element in enumerate(container_elements):
            container_scraper = self._container_scraper(cont_element, self._driver)
        
            logger.info(f"Scraping container no.{idx + 1}")
            logger.info("Getting ID...")
            container_id = container_scraper.get_id()
            logger.info("Getting Status...")
            container_status = container_scraper.get_status()
            logger.info("Getting milestones...")
            milestone_elements = container_scraper.get_milestone_elements()
            
            milestones_data = {"Gate in": None,
                              "Departure": None,
                              "Arrival": None,
                              "Discharge": None,
                              "Gate out": None,
                              "Departure Vessel Name": None,
                              "Departure Voyage ID": None,
                              "Arrival Vessel Name": None,
                              "Arrival Voyage ID": None}
            
            
            for m_element in milestone_elements:
                milestone_scraper = self._milestone_scraper(m_element)
                #self._driver.execute_script("arguments[0].scrollIntoView({ behavior: 'smooth', block: 'center' });", m_element)
                m_event = milestone_scraper.get_event()
                if (m_event not in STANDARD_EVENTS):
                    continue
                m_date = milestone_scraper.get_date()
                m_vessel = milestone_scraper.get_vessel()

                if (milestones_data[m_event] is not None and m_event not in ["Gate in", "Departure"]) or (milestones_data[m_event] is None):
                    milestones_data[m_event] = m_date
                    if m_event in ["Arrival", "Departure"]:
                        milestones_data[f"{m_event} Vessel Name"] = m_vessel[1]
                        milestones_data[f"{m_event} Voyage ID"] = m_vessel[0]

            estimated_time_arrival = milestones_data.get('Arrival', 'Unavailable')
            if container_status == 'On-going':
                for event_data in ["Arrival", "Arrival Vessel Name", "Arrival Voyage ID", "Discharge", "Gate out"]:
                    milestones_data[event_data] = None

            current_time = self._scrape_time.get_current_time()
            
            self.current_data = {
                "Scrape Time": current_time,
                "Shipment ID": shipment_id,
                "Container ID": container_id, 
                "Status": container_status,
                "ETA": estimated_time_arrival
            } | milestones_data

        