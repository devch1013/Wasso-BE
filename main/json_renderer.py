from rest_framework.renderers import JSONRenderer
from rest_framework.status import is_success


class CustomJSONRenderer(JSONRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        status_code = renderer_context["response"].status_code

        if data is None:
            data = {}

        response = {
            "status": status_code,
            "message": "success" if is_success(status_code) else "error",
            "data": data,
        }

        # Handle error messages
        if not is_success(status_code):
            response["data"] = None
            response["error"] = data

        return super().render(response, accepted_media_type, renderer_context)
