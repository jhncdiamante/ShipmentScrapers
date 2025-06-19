from fake_useragent import UserAgent
from Driver.NormalDriver import NormalDriver


class MaskedUserAgentDriver(NormalDriver):
    def set_up_driver(self):
        super().set_up_driver()

        # Set random user agent
        self._driver.execute_cdp_cmd(
            "Network.setUserAgentOverride", {"userAgent": UserAgent().random}
        )
