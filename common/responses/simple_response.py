from rest_framework.response import Response
from rest_framework import status

class SimpleResponse(Response):
    def __init__(self, message: str, status: int = status.HTTP_200_OK):
        super().__init__(
            {
                "status": status,
                "message": message,
            },
            status=status,
        )
