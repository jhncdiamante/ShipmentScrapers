from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from Container.IContainer import IContainerScraper
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from Helpers.retryable import retryable
from selenium.common.exceptions import NoSuchElementException, TimeoutException

CONTAINER_CELL_XPATH = "./td[4]"
STATUS_CELL_XPATH = "./td[9]"

TIMEOUT = 30
DETAIL_INFO_ID = "//*[@id='detail']"
CONTAINER_LINK_XPATH = "./a"
MILESTONE_ROW_XPATH = "./tr"


class OneContainerScraper(IContainerScraper):
    def __init__(self, container_element: WebElement, page: WebDriver):
        self._container_element = container_element
        self._page = page

    def get_estimated_time_arrival(self):
        pass

    def get_id(self):
        return self.get_container_id_cell().get_attribute("title")
    
    @retryable(max_retries=3, delay=2, exceptions=(NoSuchElementException,))
    def get_container_id_cell(self):
        return self._container_element.find_element(By.XPATH, CONTAINER_CELL_XPATH)

    @retryable(max_retries=3, delay=2, exceptions=(NoSuchElementException,))
    def get_status(self):
        status = self._container_element.find_element(By.XPATH, STATUS_CELL_XPATH).text.strip().lower()
        return "Completed" if status.startswith("empty") else "On-going"
    
    @retryable(max_retries=3, delay=2, exceptions=(TimeoutException,))
    def open_container_details(self):
        container_cell = self.get_container_id_cell()
        container_link = WebDriverWait(container_cell, TIMEOUT).until(
                EC.element_to_be_clickable((By.XPATH, CONTAINER_LINK_XPATH))
            )
        container_link.click()
        time.sleep(2)
    
    @retryable(max_retries=3, delay=2, exceptions=(TimeoutException,))
    def get_milestone_elements(self):
        self.open_container_details()
        milestone_table = WebDriverWait(self._page, TIMEOUT).until(
                EC.visibility_of_element_located((By.XPATH, DETAIL_INFO_ID))
            ).find_element(By.XPATH, "./tbody")
        
        milestones = WebDriverWait(milestone_table, TIMEOUT).until(
                EC.visibility_of_all_elements_located((By.XPATH, MILESTONE_ROW_XPATH))
            )   
        return milestones
