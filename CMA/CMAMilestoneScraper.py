from Milestone.IMilestone import IMilestoneScraper
from typing import Tuple, Optional
import re
from typing import Optional, Tuple
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selenium.common.exceptions import NoSuchElementException


VESSEL_VOYAGE_CSS_SELECTOR = "td.vesselVoyage.k-table-td"
VESSEL_NAME_XPATH = ".//a[1]"
VESSEL_REFERENCE_XPATH = ".//a[2]"
DATE_CSS_SELECTOR = ".calendar"
TIME_CSS_SELECTOR = ".time"
TIMEOUT = 30
EVENT_CSS_SELECTOR = "span.capsule"


class CMAMilestoneScraper(IMilestoneScraper):
    _milestone_element: WebElement
    def __init__(self, milestone_element):
        self._milestone_element = milestone_element

    def get_vessel(self) -> Tuple[Optional[str], Optional[str]]:
        try:
            vessel_voyage_element = self._milestone_element.find_element(
                By.CSS_SELECTOR, VESSEL_VOYAGE_CSS_SELECTOR
            )

            vessel_name = vessel_voyage_element.find_element(
                By.XPATH, VESSEL_NAME_XPATH
            ).text.strip()

            voyage_reference = vessel_voyage_element.find_element(
                By.XPATH, VESSEL_REFERENCE_XPATH
            ).text
            match = re.search(r"\(\s*(\S+)\)", voyage_reference)

            voyage_reference = match.group(1) if match else ""
        except NoSuchElementException:
            voyage_reference = None
            vessel_name = None

        return voyage_reference, vessel_name

    def get_event(self) -> str:
        event = (
            WebDriverWait(self._milestone_element, TIMEOUT)
            .until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, EVENT_CSS_SELECTOR))
            )
            .text.strip()
        )
        return self._normalize_event(event)

    def get_date(self) -> str:
        date_time_element = WebDriverWait(self._milestone_element, TIMEOUT).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "td.date.k-table-td"))
        )

        date = (
            date_time_element.find_element(
                By.CSS_SELECTOR, DATE_CSS_SELECTOR
            ).text.strip()
            + " "
            + date_time_element.find_element(
                By.CSS_SELECTOR, TIME_CSS_SELECTOR
            ).text.strip()
        )

        return date.split(',', 1)[1].strip()

    def _normalize_event(self, event: str) -> str:
        events = {
            "READY TO BE LOADED": "Gate in",
            "VESSEL DEPARTURE": "Departure",
            "VESSEL ARRIVAL": "Arrival",
            "DISCHARGED": "Discharge",
            "CONTAINER TO CONSIGNEE": "Gate out",
            "LOADED ON BOARD": "Gate in",  # for vietnam milestones
        }

        return events.get(event.strip().upper(), event)
