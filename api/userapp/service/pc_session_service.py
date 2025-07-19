from uuid import uuid4


class PcSessionService:
    @classmethod
    def create_session(cls):
        code = uuid4()
        return code
