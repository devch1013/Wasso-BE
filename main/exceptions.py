from enum import Enum

from rest_framework import status


class ErrorCode(Enum):
    ## 공통 에러
    NOT_IMPLEMENTED = ("서버 에러입니다", "SE001", status.HTTP_501_NOT_IMPLEMENTED)
    PARAMS_MISSING = (
        "필수 파라미터가 누락되었습니다",
        "CE002",
        status.HTTP_400_BAD_REQUEST,
    )
    ## 클럽 관련
    CLUB_ALREADY_EXISTS = (
        "이미 존재하는 클럽입니다",
        "CE001",
        status.HTTP_400_BAD_REQUEST,
    )
    ## 기수 관련
    GENERATION_NOT_FOUND = (
        "존재하지 않는 기수입니다",
        "CE003",
        status.HTTP_400_BAD_REQUEST,
    )
    ALREADY_APPLIED = (
        "이미 신청한 기수입니다",
        "CE004",
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
