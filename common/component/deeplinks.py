from enum import Enum


class DeepLink(Enum):
    MAIN = "wasso://deeplink/event"
    EVENT = "wasso://deeplink/event/{event_id}"
    ABSENT_APPLY = "wasso://deeplink/event/{event_id}/attendance"
    CLUB_APPLY = "wasso://deeplink/club/apply"

    def get_url(self, **kwargs) -> str:
        return self.value.format(**kwargs)
