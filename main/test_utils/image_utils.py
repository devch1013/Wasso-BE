import io

from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image


class ImageTestUtils:
    @staticmethod
    def create_test_image() -> SimpleUploadedFile:
        image = Image.new("RGB", (100, 100), color="red")
        image_io = io.BytesIO()
        image.save(image_io, format="PNG")
        image_io.seek(0)

        test_image = SimpleUploadedFile(
            name="test.png", content=image_io.getvalue(), content_type="image/png"
        )
        return test_image
