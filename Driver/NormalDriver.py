from selenium.webdriver.chrome.options import Options
from Driver.IDriver import IDriver
import undetected_chromedriver as uc

class NormalDriver(IDriver):
    def __init__(self):
        self._driver = None
        self.chrome_options = Options()

    def set_up_options(self):
        args = [
            "--disable-gpu", "--ignore-certificate-errors", "--ignore-ssl-errors=yes",
            "--disable-web-security", "--allow-running-insecure-content", "--log-level=3",
            "--no-sandbox", "--enable-unsafe-swiftshader", "--disable-dev-shm-usage",
            "--window-size=1920,1080", "--disable-browser-side-navigation",
            "--disable-features=VizDisplayCompositor", "--disable-blink-features=AutomationControlled",
            "--disable-extensions", "--disable-infobars"
        ]
        for arg in args:
            self.chrome_options.add_argument(arg)

    @property
    def driver(self):
        return self._driver

    @driver.setter
    def driver(self, driver):
        self._driver = driver

    def set_up_driver(self):
        self.set_up_options()
        self._driver = uc.Chrome(options=self.chrome_options, use_subprocess=True)
        
        '''self._driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
                // Remove webdriver flag
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });

                // Fake the chrome object
                window.chrome = {
                    runtime: {}
                };

                // Fake languages
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['en-US', 'en']
                });

                // Fake plugins
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5]
                });
            """
        })'''

