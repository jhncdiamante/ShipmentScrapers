from Date.IDate import IDate
from datetime import datetime

class ScrapeTime(IDate):
    def get_current_time(self):
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')