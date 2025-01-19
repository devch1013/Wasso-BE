from loguru import logger
from rest_framework.response import Response
from rest_framework.views import exception_handler

from main.exceptions import CustomException


def custom_exception_handler(exc, context):
    logger.error(f"Exception: {exc}")

    if isinstance(exc, CustomException):
        return Response(
            {
                "status": exc.status_code,
                "message": exc.message,
                "code": exc.code,
            },
            status=exc.status_code,
        )

    return exception_handler(exc, context)
