import uuid

from django.contrib.postgres.fields import ArrayField
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db import models
from django.utils import timezone
from storages.backends.s3boto3 import S3Boto3Storage

from club.models import Generation

from .enums import AttendanceType


def event_image_path(instance, filename):
    # 파일 확장자 추출
    ext = filename.split(".")[-1]
    # UUID + 확장자로 새 파일명 생성
    filename = f"{uuid.uuid4()}.{ext}"
    return f"event_images/{filename}"


class Event(models.Model):
    generation = models.ForeignKey(Generation, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    date = models.DateField(default=timezone.now)
    start_time = models.TimeField()
    end_time = models.TimeField()
    start_minutes = models.IntegerField()
    late_minutes = models.IntegerField()
    fail_minutes = models.IntegerField()
    location = models.CharField(max_length=255)
    qr_code_url = models.CharField(max_length=255)
    qr_code = models.CharField(max_length=15)
    images = ArrayField(
        models.ImageField(
            upload_to=event_image_path,
            storage=S3Boto3Storage(),
        ),
        blank=True,
        null=True,
        default=list,
    )
    attendance_type = models.CharField(max_length=10, choices=AttendanceType.choices)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "events"

    def save(self, *args, **kwargs):
        if self.images and isinstance(self.images[0], InMemoryUploadedFile):
            # Convert uploaded files to S3 URLs
            s3_urls = []
            for image in self.images:
                # Save image to S3 and get the URL
                image_name = event_image_path(self, image.name)
                storage = S3Boto3Storage()
                storage.save(image_name, image)
                s3_urls.append(image_name)

            # Update images field with S3 URLs
            self.images = s3_urls

        super().save(*args, **kwargs)
