from Website.TrackingWebsite import TrackingWebsite
from Helpers.logging_config import setup_logger
from collections import deque
logger = setup_logger()


class MaerskWebsite(TrackingWebsite):

    def _process_milestones(self, container) -> list:
        milestones = container.get_milestone_elements()
        milestones_data = []
        for terminal in container.get_terminals():
            milestones_data.extend(self._match_milestones_to_terminal(terminal, milestones))

        return milestones_data
    

    def _match_milestones_to_terminal(self, terminal_name: str, milestones: deque) -> list:
        matched = []
        while milestones:
            milestone = self._milestone_scraper(milestones[0])
            m_location = milestone.get_location()
            if m_location and m_location.lower() not in terminal_name.lower():
                break

            event = milestone.get_event()
            voyage_id, voyage_name = milestone.get_vessel()
            milestone_date = milestone.get_date()
            matched.append({
                "event": event,
                "date": milestone_date,
                "voyage_id": voyage_id,
                "voyage_name": voyage_name,
                "location": terminal_name,
            })
            milestones.popleft()
        return matched
    
