import uuid

from django.db import models
from storages.backends.s3boto3 import S3Boto3Storage


def club_image_path(instance, filename):
    # 파일 확장자 추출
    ext = filename.split(".")[-1]
    # UUID + 확장자로 새 파일명 생성
    filename = f"{uuid.uuid4()}.{ext}"
    return f"club_profile/{filename}"


class Club(models.Model):
    def __str__(self):
        return self.name

    name = models.CharField(max_length=255)
    image = models.ImageField(
        null=True,
        blank=True,
        upload_to=club_image_path,
        storage=S3Boto3Storage(),
    )
    description = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "clubs"
