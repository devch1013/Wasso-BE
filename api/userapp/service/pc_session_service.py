from datetime import datetime, timedelta

from django.utils import timezone
from rest_framework.exceptions import PermissionDenied

from api.club.models.generation_mapping import GenMember
from api.event.models import Event
from api.userapp.enums import SessionState
from api.userapp.models import PcSession
from common.exceptions import CustomException, ErrorCode


class PcSessionService:
    @classmethod
    def create_session(cls, platform: str, user_agent: str):
        pc_session = PcSession.objects.create(
            platform=platform,
            user_agent=user_agent,
            expires_at=datetime.now() + timedelta(minutes=10),
        )
        return pc_session

    @classmethod
    def get_session_state(cls, session_id: str) -> SessionState:
        session = PcSession.objects.get(code=session_id)
        return session.state

    @classmethod
    def authenticate_session(cls, session_code: str, user, event_id: int):
        """세션을 인증하고 사용자 및 이벤트 정보를 설정"""
        try:
            session = PcSession.objects.get(code=session_code)

            # 세션이 만료되었는지 확인
            if session.expires_at < timezone.now():
                session.state = SessionState.EXPIRED
                session.save()
                raise CustomException(ErrorCode.PC_SESSION_EXPIRED)

            # 세션이 이미 사용되었는지 확인
            if session.state != SessionState.PENDING:
                raise CustomException(ErrorCode.PC_SESSION_ALREADY_USED)

            event = Event.objects.get(id=event_id)

            try:
                if not GenMember.objects.get(
                    member__user=user, generation__id=event.generation.id
                ).is_admin():
                    raise PermissionDenied("클럽 관리자만 이벤트를 생성할 수 있습니다.")

            except GenMember.DoesNotExist:
                raise PermissionDenied("클럽 관리자만 이벤트를 생성할 수 있습니다.")

            # 세션 인증
            session.user = user
            session.event = event
            session.state = SessionState.AUTHENTICATED
            session.save()

            return session
        except PcSession.DoesNotExist:
            raise CustomException(ErrorCode.PC_SESSION_NOT_FOUND)
        except Event.DoesNotExist:
            raise CustomException(ErrorCode.PC_SESSION_NOT_FOUND)
