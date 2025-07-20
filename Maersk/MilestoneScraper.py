from Milestone.IMilestone import IMilestoneScraper
from typing import Tuple, Optional
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
import re


class MaerskMilestoneScraper(IMilestoneScraper):
    def __init__(self, milestone_element: WebElement):
        self._milestone_element = milestone_element

    def get_date(self) -> str:
        return self._milestone_element.find_element(
            By.CSS_SELECTOR, "span[data-test='milestone-date']"
        ).text.strip()

    def get_event(self) -> str:
        event = self._milestone_element.find_element(By.TAG_NAME, "span").text.strip()
        if "vessel arrival" in event.lower():
            return "Arrival"
        elif "departure" in event.lower():
            return "Departure"
        elif "gate out" in event.lower():
            return "Gate out"
        return event

    def get_vessel(self) -> Tuple[Optional[str], Optional[str]]:
        match = re.search(r"\((.+?) / (\w+)\)", self._milestone_element.text.strip())
        if match:
            vessel_name = match.group(1).strip()
            voyage_id = match.group(2).strip()
            return voyage_id, vessel_name
        return None, None
