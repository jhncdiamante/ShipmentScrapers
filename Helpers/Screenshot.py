from pathlib import Path
from selenium.webdriver.remote.webdriver import WebDriver

USER_PATH = Path.home() / "shipment_tracker_screenshots"

def screenshot(driver: WebDriver, shipment_provider: str, bl_number: str, container_number: str) -> Path:
    # Folder: ~/shipment_tracker_screenshots/screenshots/<shipment_provider>/<bl_number>/
    folder = USER_PATH / "screenshots" / shipment_provider / bl_number
    folder.mkdir(parents=True, exist_ok=True)  # create full path if missing

    # File path
    file_path = folder / f"{container_number}.png"

    # Save screenshot
    driver.save_screenshot(str(file_path))

    return file_path
