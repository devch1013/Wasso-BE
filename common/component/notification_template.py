from enum import Enum

class NotificationTemplate(Enum):
    CLUB_APPLY = ("동아리 가입 신청", "{username}님이 동아리 가입을 요청했습니다.")
    CLUB_APPLY_ACCEPT = ("[{club_name}] 동아리 가입 신청", "{club_name} 가입이 승인되었습니다.")
    CLUB_APPLY_REJECT = ("[{club_name}] 동아리 가입 신청", "{club_name} 가입이 거절되었습니다.")
    
    def __init__(self, title: str, body: str) -> None:
        self._title = title
        self._body = body
        
    def get_title(self, **kwargs) -> str:
        return self._title.format(**kwargs)
        
    def get_body(self, **kwargs) -> str:
        return self._body.format(**kwargs)
