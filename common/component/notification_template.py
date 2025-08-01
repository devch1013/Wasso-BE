from enum import Enum


class NotificationTemplate(Enum):
    CLUB_APPLY = ("동아리 가입 신청", "{username}님이 동아리 가입을 요청했습니다.")
    CLUB_APPLY_ACCEPT = (
        "[{club_name}] 동아리 가입 신청",
        "{club_name} 가입이 승인되었습니다.",
    )
    CLUB_APPLY_REJECT = (
        "[{club_name}] 동아리 가입 신청",
        "{club_name} 가입이 거절되었습니다.",
    )
    EVENT_CREATE = (
        "새로운 활동이 등록되었습니다.",
        "[{club_name}]에 새로운 활동이 등록되었습니다.",
    )
    ATTENDANCE_CHANGE = (
        "출석 상태가 변경되었습니다.",
        "[{event_name}] 활동의 출석 상태가 {attendance_status}으로 변경되었습니다.",
    )
    MEMBER_ROLE_CHANGE = (
        "동아리의 권한이 변경되었습니다.",
        "[{club_name}] 동아리의 권한이 {role_name}으로 변경되었습니다.",
    )
    ABSENT_APPLY = (
        "{status} 신청",
        "[{event_name}] 활동에 {username}님이 {status} 신청을 했습니다.",
    )
    ABSENT_APPLY_APPROVE = (
        "{status} 신청이 승인되었습니다.",
        "[{event_name}] 활동의 {status} 신청이 승인되었습니다.",
    )

    def __init__(self, title: str, body: str) -> None:
        self._title = title
        self._body = body

    def get_title(self, **kwargs) -> str:
        return self._title.format(**kwargs)

    def get_body(self, **kwargs) -> str:
        return self._body.format(**kwargs)
