
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.action_chains import ActionChains

from selenium.webdriver.remote.webdriver import WebDriver
from Helpers.retryable import retryable
from selenium.common.exceptions import ElementClickInterceptedException, TimeoutException, NoSuchElementException, ElementNotInteractableException

import time
import random
from Container.IContainer import IContainerScraper


from Helpers.logging_config import setup_logger

log = setup_logger()


# SuperClassContainer 
DISPLAY_PREVIOUS_EVENTS_BUTTON = 'a[aria-label="Display Previous Moves"]:not([tabindex="-1"])'
HIDE_PREVIOUS_EVENTS_BUTTON = 'a[aria-label="Hide Previous Moves"]:not([tabindex="-1"])'

REFERENCE_ROWS = '.ico.ico-truck, .ico.ico-vessel'
GRANDPARENT_ELEMENT = '../..'

# Container with siblings



HIDDEN_RESULTS_CARD_PANEL = "section.result-card--details.is-hidden" # css selector
VISIBLE_RESULTS_CARD_PANEL = "//section[@class='result-card--details']" # xpath



CWS_ETA_ELEMENT = './/div[contains(text(), "ETA Berth at POD")]/..' 
CONTAINER_WS_ID_PANEL_CSS_SELECTOR = 'section.result-card--content'
CONTAINER_WS_ID_ELEMENT_XPATH = './/dl[@class="container-ref"]/dt/span[1]'
CONTAINER_WS_DETAILS_BUTTON_CSS_SELECTOR = "section.result-card--actions label"

# Container with no siblings
CWNS_ETA_ELEMENT = "div.timeline--item-eta"
CONTAINER_WNS_ID_XPATH = "//li[starts-with(normalize-space(text()), 'Container')]"
CWNS_STATUS_CSS_SELECTOR = "span.capsule.primary"
CWS_STATUS_CSS_SELECTOR = "div.capsule.info-dark"
MILESTONE_PANEL_CSS_SELECTOR = 'section.result-card--details'
TIMEOUT = 30


class CMAContainerScraper(IContainerScraper):
    def __init__(self, container_element: WebElement | WebDriver, driver: WebDriver):
        self._container_element = container_element
        self._driver = driver

    def _goto_element(self, element):
        # Scroll the button into view
        self._driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)

    @retryable(max_retries=3, delay=2, exceptions=(TimeoutException, ElementClickInterceptedException, ElementNotInteractableException,))
    def display_previous_events(self) -> None:
        
        log.info("Attempting to click <display_prev_events> button...")
        display_previous_events_button = WebDriverWait(self._container_element, TIMEOUT).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, DISPLAY_PREVIOUS_EVENTS_BUTTON))
        )
        self._goto_element(display_previous_events_button)
        log.info("Scrolled in to button...")
        time.sleep(2)

        ActionChains(self._driver).move_to_element(display_previous_events_button).click().perform()
        log.info("Button clicked with action chains. Trying to confirm...")
        try:
            WebDriverWait(self._container_element, TIMEOUT).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, HIDE_PREVIOUS_EVENTS_BUTTON))
                )
        except TimeoutException:
            self._driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", display_previous_events_button)
            self._driver.execute_script("arguments[0].click();", display_previous_events_button)
            WebDriverWait(self._container_element, TIMEOUT).until(
                        EC.visibility_of_element_located((By.CSS_SELECTOR, HIDE_PREVIOUS_EVENTS_BUTTON))
                )
        log.info("<display_prev_events> button clicked.")
        
    


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
        print(f"Latest event: {last_event}")
        
        return "Completed" if last_event in {'empty in depot', 'container to consignee'} else "On-going"


class CMAContainerWithSiblingsScraper(CMAContainerScraper):
    
       
    def get_status(self):
        return super().get_status(CWS_STATUS_CSS_SELECTOR)
        
    @retryable(max_retries=3, delay=2, exceptions=(TimeoutException, NoSuchElementException))
    def get_estimated_time_arrival(self) -> str:
        eta_panel = WebDriverWait(self._container_element, TIMEOUT).until(
            EC.visibility_of_element_located((By.XPATH, CWS_ETA_ELEMENT))
        )
        date_spans = eta_panel.find_elements(By.TAG_NAME, "span")

        eta_info = " ".join([span.text.strip() for span in date_spans])
        return eta_info
       
    @retryable(max_retries=5, delay=2, exceptions=(TimeoutException, ElementNotInteractableException, ElementClickInterceptedException))
    def display_details(self) -> None:
        
        button = WebDriverWait(self._container_element, TIMEOUT).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, CONTAINER_WS_DETAILS_BUTTON_CSS_SELECTOR))
        )

        ActionChains(self._driver).move_to_element(button).click().perform()

        try:
            WebDriverWait(self._container_element, TIMEOUT).until(
                EC.visibility_of_element_located((By.XPATH, VISIBLE_RESULTS_CARD_PANEL))
            )
        except TimeoutException:
            self._driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", button)
            self._driver.execute_script("arguments[0].click();", button)
            WebDriverWait(self._container_element, TIMEOUT).until(
                EC.visibility_of_element_located((By.XPATH, VISIBLE_RESULTS_CARD_PANEL))
            )       
        
        log.info("<display_details_button> clicked.")

    
    @retryable(max_retries=3, delay=2, exceptions=(TimeoutException, NoSuchElementException))
    def get_id(self) -> str:
        container_id = WebDriverWait(self._container_element, TIMEOUT).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, CONTAINER_WS_ID_PANEL_CSS_SELECTOR))
        ).find_element(By.XPATH, CONTAINER_WS_ID_ELEMENT_XPATH).text.strip()
        
        return container_id

    @retryable(max_retries=5, delay=2, exceptions=(Exception,))
    def get_milestone_elements(self):
        self.display_details()
        time.sleep(random.randint(3, 5))
        self.display_previous_events()
        time.sleep(random.randint(3, 5))
        return super().get_milestone_elements()

     

class CMAContainerWithNoSiblingsScraper(CMAContainerScraper):       
       
    def get_status(self):
        return super().get_status(CWNS_STATUS_CSS_SELECTOR)

    @retryable(max_retries=3, delay=2, exceptions=(TimeoutException, NoSuchElementException))
    def get_estimated_time_arrival(self):
        eta_element = WebDriverWait(self._container_element, TIMEOUT).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, CWNS_ETA_ELEMENT))
        )
        date_element = eta_element.find_element(By.TAG_NAME, 'p')
        eta_date = date_element.text.strip()
        return eta_date

    @retryable(max_retries=3, delay=2, exceptions=(TimeoutException, NoSuchElementException))
    def get_id(self) -> str:
      
        li_element = WebDriverWait(self._container_element, TIMEOUT).until(
            EC.visibility_of_element_located((By.XPATH, CONTAINER_WNS_ID_XPATH))
        )
        container_id = li_element.find_element(By.TAG_NAME, "strong").text.strip()
        
        return container_id

    def get_milestone_elements(self):
        self.display_previous_events()
        time.sleep(random.randint(3, 5))
        return super().get_milestone_elements()
        
      
    