from enum import Enum

from rest_framework import status


class ErrorCode(Enum):
    NOT_IMPLEMENTED = ("서버 에러입니다", "SE001", status.HTTP_501_NOT_IMPLEMENTED)
    CLUB_ALREADY_EXISTS = (
        "이미 존재하는 클럽입니다",
        "CE001",
        status.HTTP_400_BAD_REQUEST,
    )

    def __init__(self, message, code, status):
        self.message = message
        self.status = status
        self.code = code


class CustomException(Exception):
    def __init__(self, error_code: ErrorCode):
        self.message = error_code.message
        self.status_code = error_code.status
        self.code = error_code.code
        super().__init__(self.message)
