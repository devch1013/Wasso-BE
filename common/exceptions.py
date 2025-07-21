from enum import Enum

from rest_framework import status


class ErrorCode(Enum):
    ## JWT 인증 관련 에러
    JWT_TOKEN_MISSING = (
        "JWT 토큰이 제공되지 않았습니다",
        "JWT001",
        status.HTTP_401_UNAUTHORIZED,
    )
    JWT_TOKEN_INVALID = (
        "유효하지 않은 JWT 토큰입니다",
        "JWT002",
        status.HTTP_401_UNAUTHORIZED,
    )
    JWT_TOKEN_EXPIRED = (
        "JWT 토큰이 만료되었습니다",
        "JWT003",
        status.HTTP_401_UNAUTHORIZED,
    )
    JWT_TOKEN_MALFORMED = (
        "잘못된 형식의 JWT 토큰입니다",
        "JWT004",
        status.HTTP_401_UNAUTHORIZED,
    )
    JWT_USER_NOT_FOUND = (
        "토큰의 사용자를 찾을 수 없습니다",
        "JWT005",
        status.HTTP_401_UNAUTHORIZED,
    )
    JWT_USER_INACTIVE = (
        "비활성화된 사용자입니다",
        "JWT006",
        status.HTTP_401_UNAUTHORIZED,
    )
    ## Refresh 토큰 관련 에러
    REFRESH_TOKEN_MISSING = (
        "Refresh 토큰이 제공되지 않았습니다",
        "RT001",
        status.HTTP_401_UNAUTHORIZED,
    )
    REFRESH_TOKEN_INVALID = (
        "유효하지 않은 Refresh 토큰입니다",
        "RT002",
        status.HTTP_401_UNAUTHORIZED,
    )
    REFRESH_TOKEN_EXPIRED = (
        "Refresh 토큰이 만료되었습니다",
        "RT003",
        status.HTTP_401_UNAUTHORIZED,
    )
    REFRESH_TOKEN_BLACKLISTED = (
        "이미 사용된 Refresh 토큰입니다",
        "RT004",
        status.HTTP_401_UNAUTHORIZED,
    )
    ## 소셜로그인 관련 에러
    INVALID_TOKEN = ("유효하지 않은 토큰입니다", "SE001", status.HTTP_401_UNAUTHORIZED)
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
    ALREADY_CHECKED = (
        "이미 출석 체크를 완료하였습니다",
        "CE005",
        status.HTTP_400_BAD_REQUEST,
    )
    INVALID_TIME = (
        "출석 체크 시간이 아닙니다",
        "CE006",
        status.HTTP_400_BAD_REQUEST,
    )
    INVALID_QR_CODE = (
        "유효하지 않은 QR 코드입니다",
        "CE007",
        status.HTTP_400_BAD_REQUEST,
    )
    APPLY_NOT_FOUND = (
        "존재하지 않는 가입 신청입니다",
        "CE008",
        status.HTTP_400_BAD_REQUEST,
    )
    ROLE_NOT_FOUND = (
        "존재하지 않는 역할입니다",
        "CE009",
        status.HTTP_400_BAD_REQUEST,
    )
    OWNER_ROLE_MUST_BE_MORE_THAN_ONE = (
        "모든 권한을 가진 역할은 최소 한 개 이상 존재해야 합니다",
        "CE010",
        status.HTTP_400_BAD_REQUEST,
    )
    OWNER_CANNOT_BE_DELETED = (
        "모든 권한을 가진 역할은 삭제할 수 없습니다",
        "CE011",
        status.HTTP_400_BAD_REQUEST,
    )
    ## PC 세션 관련 에러
    PC_SESSION_EXPIRED = (
        "PC 세션이 만료되었습니다",
        "PC001",
        status.HTTP_400_BAD_REQUEST,
    )
    PC_SESSION_ALREADY_USED = (
        "PC 세션이 이미 사용되었습니다",
        "PC002",
        status.HTTP_400_BAD_REQUEST,
    )
    PC_SESSION_NOT_FOUND = (
        "PC 세션을 찾을 수 없습니다",
        "PC003",
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
