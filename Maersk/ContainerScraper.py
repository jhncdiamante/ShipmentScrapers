from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.remote.webelement import WebElement
from Container.IContainer import IContainerScraper
from Button.IButton import IButton
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from Maersk.ContainerExpandButton import MaerskContainerExpandButton
from Helpers.retryable import retryable

from Helpers.logging_config import setup_logger
import time, random

logging = setup_logger()

TIMEOUT = 60
CONTAINER_TOGGLE_BUTTON_CSS_SELECTOR = ".container__toggle.toggle-button"
CONTAINER_STATUS_CSS_SELECTOR = (
    'mc-text-and-icon[data-test="container-location"] > span[slot="sublabel"]'
)
EVENT_DETERMINER_FOR_STATUS = "empty container return"
COMPLETED_CONTAINER = "Completed"
IN_PROGRESS_CONTAINER = "On-going"
DEFAULT_MILESTONE_PANEL_ID = "transport-plan__container__0"
ETA_HOST_ELEMENT_CSS_SELECTOR = 'mc-text-and-icon[data-test="container-eta"]'
ETA_CSS_SELECTOR = 'slot[name="sublabel"].sublabel'


class MaerskContainerScraper(IContainerScraper):
    _container_element: WebElement
    _page_handle: WebDriver
    _expand_button: IButton
    def __init__(self, container_element, page_handle):
        self._container_element = container_element
        self._page_handle = page_handle
        self._expand_button = self._get_expand_button()

    def _get_expand_button(self) -> IButton:
        return MaerskContainerExpandButton(
            (By.CSS_SELECTOR, CONTAINER_TOGGLE_BUTTON_CSS_SELECTOR),
            self._container_element,
            self._page_handle
        )

    @retryable(max_retries=5, delay=2, exceptions=(TimeoutException,))
    def get_id(self) -> str:
        container_id_element = WebDriverWait(self._container_element, 60).until(
            EC.visibility_of_element_located((By.TAG_NAME, "span"))
        )
        container_id = container_id_element.text.strip()
        logging.info(f"Successfully extracted container ID: {container_id}")
        return container_id

    @retryable(max_retries=3, delay=2, exceptions=(TimeoutException,))
    def get_status(self) -> str:
        element = WebDriverWait(self._container_element, TIMEOUT).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, CONTAINER_STATUS_CSS_SELECTOR)
            )
        )
        logging.info("Determining container status...")
        return (
            COMPLETED_CONTAINER
            if EVENT_DETERMINER_FOR_STATUS in element.text.strip().lower()
            else IN_PROGRESS_CONTAINER
        )

    @retryable(max_retries=5, delay=2, exceptions=(TimeoutException,))
    def get_milestone_elements(self) -> list[WebElement]:
        try:
            # try clicking expand button if present and not yet expanded
            if not self._expand_button.get_state():
                self._expand_button.click()
                # time.sleep(random.randint(3, 5))
            # get the milestone panel ref located in expand button attributes
            milestone_panel_id = self._expand_button.get_panel_reference()
        except TimeoutException:
            milestone_panel_id = DEFAULT_MILESTONE_PANEL_ID  # default id ref, usually,
            # first containers don't have expand button where we can extract the milestone panel ref

        milestone_panel = WebDriverWait(self._container_element, TIMEOUT).until(
            EC.visibility_of_element_located((By.ID, milestone_panel_id))
        )  # fetch the panel where milestones are located

        m_elements = WebDriverWait(milestone_panel, TIMEOUT).until(
            EC.visibility_of_all_elements_located((By.CLASS_NAME, "milestone"))
        )  # get all milestone elements
        return m_elements

    @retryable(
        max_retries=3, delay=2, exceptions=(TimeoutException, NoSuchElementException)
    )
    def get_estimated_time_arrival(self) -> str:
        host = WebDriverWait(self._container_element, TIMEOUT).until(
            EC.visibility_of_element_located(
                (By.CSS_SELECTOR, ETA_HOST_ELEMENT_CSS_SELECTOR)
            )
        )
        shadow_root = self._page_handle.execute_script(
            "return arguments[0].shadowRoot", host
        )
        estimated_arrival_date = shadow_root.find_element(
            By.CSS_SELECTOR, ETA_CSS_SELECTOR
        )
        return estimated_arrival_date.text.strip()
