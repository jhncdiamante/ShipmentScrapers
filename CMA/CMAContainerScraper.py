
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement

from selenium.webdriver.remote.webdriver import WebDriver
from Helpers.retryable import retryable
from selenium.common.exceptions import ElementClickInterceptedException, TimeoutException, NoSuchElementException, ElementNotInteractableException

import time
import random
from Container.IContainer import IContainerScraper
# SuperClassContainer 
DISPLAY_PREVIOUS_EVENTS_BUTTON = 'a[aria-label="Display Previous Moves"]'
REFERENCE_ROWS = '.ico.ico-truck, .ico.ico-vessel'
GRANDPARENT_ELEMENT = '../..'

# Container with siblings
ETA_ELEMENT = './/div[contains(text(), "ETA Berth at POD")]/..' 
CONTAINER_WS_ID_PANEL_CSS_SELECTOR = 'section.result-card--content'
CONTAINER_WS_ID_ELEMENT_XPATH = './/dl[@class="container-ref"]/dt/span[1]'
CONTAINER_WS_DETAILS_BUTTON_CSS_SELECTOR = "section.result-card--actions"

# Container with no siblings
CONTAINER_WNS_ID_XPATH = "//li[starts-with(normalize-space(text()), 'Container')]"
CWNS_STATUS_CSS_SELECTOR = "span.capsule.primary"
CWS_STATUS_CSS_SELECTOR = "div.capsule.info-dark"

TIMEOUT = 30


class CMAContainerScraper(IContainerScraper):
    def __init__(self, container_element: WebElement | WebDriver, driver: WebDriver):
        self._container_element = container_element
        self._driver = driver


    @retryable(max_retries=3, delay=2, exceptions=(TimeoutException, ElementClickInterceptedException, ElementNotInteractableException,))
    def display_previous_events(self) -> None:
        display_previous_events_button = WebDriverWait(self._container_element, TIMEOUT).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, DISPLAY_PREVIOUS_EVENTS_BUTTON))
        )
        display_previous_events_button.click()
        time.sleep(random.randint(5, 10)) # wait for DOM changes

    @retryable(max_retries=3, delay=2, exceptions=(TimeoutException, NoSuchElementException,))
    def get_milestone_elements(self):
        # milestone elements have a complex hierarchy but
        # event element has a sibling with span children containing truck or vessel icon
        # so we can use the truck or vessel icon to identify the event parent element(milestone row element)
        ref_rows = WebDriverWait(self._container_element, TIMEOUT).until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, REFERENCE_ROWS)))
        
        milestone_rows = [row.find_element(By.XPATH, GRANDPARENT_ELEMENT) for row in ref_rows]
        
        return milestone_rows
        

    @retryable(max_retries=3, delay=2, exceptions=(TimeoutException,))
    def get_status(self, last_event_css_selector):
        last_event_element = WebDriverWait(self._container_element, TIMEOUT).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, last_event_css_selector))
        )
        last_event = last_event_element.text.strip().lower()
        
        return "Completed" if last_event == 'empty in depot' else "On-going"



class CMAContainerWithSiblingsScraper(CMAContainerScraper):
    
       
    def get_status(self):
        return super().get_status(CWS_STATUS_CSS_SELECTOR)
        
    @retryable(max_retries=3, delay=2, exceptions=(TimeoutException, NoSuchElementException))
    def get_estimated_time_arrival(self) -> str:
        eta_panel = WebDriverWait(self._container_element, TIMEOUT).until(
            EC.visibility_of_element_located((By.XPATH, ETA_ELEMENT))
        )
        date_spans = eta_panel.find_elements(By.TAG_NAME, "span")

        eta_info = " ".join([span.text.strip() for span in date_spans])
        return eta_info
       
    @retryable(max_retries=3, delay=2, exceptions=(TimeoutException, NoSuchElementException, ElementNotInteractableException, ElementClickInterceptedException))
    def display_details(self) -> None:
       
        button = WebDriverWait(self._container_element, TIMEOUT).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, CONTAINER_WS_DETAILS_BUTTON_CSS_SELECTOR))
        )
        button.find_element(By.CSS_SELECTOR, "label").click()
    
    @retryable(max_retries=3, delay=2, exceptions=(TimeoutException, NoSuchElementException))
    def get_id(self) -> str:
        container_id = WebDriverWait(self._container_element, TIMEOUT).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, CONTAINER_WS_ID_PANEL_CSS_SELECTOR))
        ).find_element(By.XPATH, CONTAINER_WS_ID_ELEMENT_XPATH).text.strip()
        
        return container_id

    def get_milestone_elements(self):
        self.display_details()
        self.display_previous_events()
        return super().get_milestone_elements()

     

class CMAContainerWithNoSiblingsScraper(CMAContainerScraper):       
       
    def get_status(self):
        return super().get_status(CWNS_STATUS_CSS_SELECTOR)

    
    def get_estimated_time_arrival(self):
        return "Data Unavailable"

    @retryable(max_retries=3, delay=2, exceptions=(TimeoutException, NoSuchElementException))
    def get_id(self) -> str:
      
        li_element = WebDriverWait(self._container_element, TIMEOUT).until(
            EC.visibility_of_element_located((By.XPATH, CONTAINER_WNS_ID_XPATH))
        )
        container_id = li_element.find_element(By.TAG_NAME, "strong").text.strip()
        
        return container_id

    def get_milestone_elements(self):
        self.display_previous_events()
        return super().get_milestone_elements()
        
      
    