from rest_framework.response import Response


class SimpleResponse(Response):
    def __init__(self, message: str, status_code: int = 200):
        super().__init__(
            {
                "status": status_code,
                "message": message,
            },
            status=status_code,
        )
