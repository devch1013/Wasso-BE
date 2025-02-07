import uuid
from urllib.parse import urlparse

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


def event_qr_code_path(instance, filename):
    return f"event_qr_codes/{filename}"


class Event(models.Model):
    generation = models.ForeignKey(Generation, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.CharField(max_length=255, null=True, blank=True)
    date = models.DateField(default=timezone.now)
    start_time = models.TimeField()
    end_time = models.TimeField()
    start_minutes = models.IntegerField()
    late_minutes = models.IntegerField()
    fail_minutes = models.IntegerField()
    location = models.CharField(max_length=255)
    qr_code_url = models.ImageField(
        upload_to=event_qr_code_path, null=True, blank=True, storage=S3Boto3Storage()
    )
    qr_code = models.CharField(max_length=50, null=True, blank=True)
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

    def update_images(self, new_images: list, deleted_images: list):
        """
        기존 이미지 리스트에 새로운 이미지들을 추가합니다.
        :param new_images: 새로 추가할 이미지 파일 리스트
        """
        if deleted_images is None:
            deleted_images = []
        if new_images is None:
            new_images = []

        # URL에서 path 부분만 추출 (도메인 제거)
        deleted_images = [urlparse(image).path.lstrip("/") for image in deleted_images]

        # 기존 이미지 URL 리스트 보존
        existing_images = self.images or []
        existing_images = [
            image for image in existing_images if image not in deleted_images
        ]

        # 새로운 이미지들을 S3에 업로드하고 URL 얻기
        s3_urls = []
        storage = S3Boto3Storage()
        for image in new_images:
            if isinstance(image, InMemoryUploadedFile):
                image_name = event_image_path(self, image.name)
                storage.save(image_name, image)
                s3_urls.append(image_name)

        # 기존 이미지 URL들과 새로운 이미지 URL들을 합치기
        self.images = existing_images + s3_urls
