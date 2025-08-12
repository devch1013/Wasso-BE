from enum import Enum


class DeepLink(Enum):
    MAIN = "wasso://deeplink/event"
    EVENT = "wasso://deeplink/event/{event_id}"

    def get_url(self, **kwargs) -> str:
        return self.value.format(**kwargs)
