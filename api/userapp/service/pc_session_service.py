from datetime import datetime, timedelta

from api.userapp.enums import SessionState
from api.userapp.models import PcSession


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
