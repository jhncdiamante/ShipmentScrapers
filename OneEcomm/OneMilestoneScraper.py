from Milestone.IMilestone import IMilestoneScraper
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

# Constants for event mapping
EVENTS = [
    ("gate in", "Gate in"),
    ("departure from port of loading", "Departure"),
    ("arrival at port of discharging", "Arrival"),
    ("gate out", "Gate out"),
]

# XPath/selectors
EVENT_CELL_XPATH = "./td[2]"
DATE_CELL_XPATH = "./td[4]"
LOCATION_CELL_XPATH = "./td[3]"
VESSEL_LINK_XPATH = "./a"


class OneMilestoneScraper(IMilestoneScraper):
    _milestone_element: WebElement
    def __init__(self, milestone_element):
        self._milestone_element = milestone_element

    def get_date(self):
        date = self._milestone_element.find_element(By.XPATH, DATE_CELL_XPATH).text
        return " ".join(date.split()[1:]) if date else "No Date Available"

    def get_event(self):
        event = self._milestone_element.find_element(By.XPATH, EVENT_CELL_XPATH)
        return self._normalize_event(event.text.split("\n")[0])

    def get_vessel(self):
        try:
            event_element = self._milestone_element.find_element(
                By.XPATH, EVENT_CELL_XPATH
            )
            vessel = event_element.find_element(By.XPATH, VESSEL_LINK_XPATH)
            vessel_name, vessel_id = (
                vessel.get_attribute("title"),
                vessel.text.split()[-1],
            )
            return vessel_id, vessel_name
        except NoSuchElementException:
            return None, None

    def _normalize_event(self, event) -> str:
        match_string = event.lower().strip()

        if match_string.startswith("unloaded") and match_string.endswith("discharging"):
            return "Discharge"

        for event_pattern, event_name in EVENTS:
            if event_pattern in match_string:
                return event_name
        return event

    def get_location(self) -> str:
        return self._milestone_element.find_element(By.XPATH, LOCATION_CELL_XPATH).text.strip()
        