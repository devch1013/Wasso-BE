import io

from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image


class ImageTestUtils:
    @classmethod
    def create_test_image(cls, width=100, height=100) -> SimpleUploadedFile:
        image = Image.new("RGB", (width, height), color="red")
        image_io = io.BytesIO()
        image.save(image_io, format="PNG")
        image_io.seek(0)

        test_image = SimpleUploadedFile(
            name="test.png", content=image_io.getvalue(), content_type="image/png"
        )
        return test_image
