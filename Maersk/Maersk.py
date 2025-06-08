from Driver.MaskedUserAgentDriver import MaskedUserAgentDriver
from Maersk.MaerskSearchBar import MaerskSearchBar
from Button.Button import Button
from Search.SearchFeature import SearchFeature
from CookiesManager.CookieHandler import CookieHandler
from Website.TrackingWebsite import TrackingWebsite
from Maersk.MaerskShipment import MaerskShipmentScraper
from Maersk.ContainerScraper import MaerskContainerScraper
from Maersk.MilestoneScraper import MaerskMilestoneScraper
from Database.CSVDatabase import CsvObserver
from selenium.webdriver.common.by import By
from Date.ScrapeTime import ScrapeTime
from Helpers.logging_config import setup_logger, log_scraper_action, log_error
import pandas as pd
import time, random

# Setup logger for this module
logger = setup_logger('maersk_scraper')

try:
    log_scraper_action(logger, "Starting Maersk Scraper", {"scraper": "Maersk"})

    INPUT_FILE_PATH = r"D:\vscode\Maersk\OUTPUT.csv"
    OUTPUT_FILE_PATH = r"MAERSK_OUTPUT.csv"

    log_scraper_action(logger, "Reading input file", {"file_path": INPUT_FILE_PATH})

    if INPUT_FILE_PATH.endswith(".csv"):
        df = pd.read_csv(INPUT_FILE_PATH)
    elif INPUT_FILE_PATH.endswith(".xlsx"):
        df = pd.read_excel(INPUT_FILE_PATH)
        
    # Convert the first column to a list of BL numbers
    first_col_list = df.iloc[:, 0].dropna().unique().tolist()
    log_scraper_action(logger, "Extracted booking numbers", {"count": len(first_col_list)})

    log_scraper_action(logger, "Initializing web driver")
    maersk_driver_handle = MaskedUserAgentDriver()
    maersk_driver_handle.set_up_driver()
    maersk_driver = maersk_driver_handle.driver 

    search_bar = MaerskSearchBar(maersk_driver, (By.CSS_SELECTOR, "mc-input#track-input")) 
    search_button = Button((By.CLASS_NAME, "track__search__button"), maersk_driver)
    search_feature = SearchFeature(search_bar=search_bar, search_button=search_button)
    allow_button = Button((
                    By.CSS_SELECTOR, "button[data-test='coi-allow-all-button']"
                ), maersk_driver)
    cookie_handler = CookieHandler(maersk_driver, allow_cookies_button=allow_button)
    scrape_time = ScrapeTime()
    
    log_scraper_action(logger, "Setting up tracking website")
    maersk = TrackingWebsite("https://www.maersk.com/tracking/", maersk_driver, search_feature, cookie_handler,
                                shipment_scraper_factory=MaerskShipmentScraper,
                                container_scraper_factory=MaerskContainerScraper,
                                milestone_scraper_factory=MaerskMilestoneScraper,
                                scrape_time=scrape_time)
    csv_observer = CsvObserver(OUTPUT_FILE_PATH)
    maersk.attach(csv_observer)
    
    log_scraper_action(logger, "Opening tracking website")
    maersk.open()
    
    for shipment_id in first_col_list:
        try:
            log_scraper_action(logger, "Processing shipment", {"shipment_id": shipment_id})
            maersk.track_shipment(shipment_id)
            time.sleep(random.randint(3,5))
        except Exception as e:
            log_error(logger, e, {"shipment_id": shipment_id})
            continue

except Exception as e:
    log_error(logger, e, {"context": "Main scraper execution"})
finally:
    if 'maersk_driver' in locals():
        log_scraper_action(logger, "Closing web driver")
        maersk_driver.quit()
    log_scraper_action(logger, "Maersk scraper completed")