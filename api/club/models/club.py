import uuid

from django.db import models
from django.utils import timezone
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
    short_description = models.TextField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    current_generation = models.ForeignKey(
        "Generation",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="current_club",
    )

    default_role = models.ForeignKey(
        "Role",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="default_club",
    )
    notion_database_id = models.CharField(max_length=255, null=True, blank=True)

    deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def delete(self):
        self.deleted = True
        self.deleted_at = timezone.localtime(timezone.now())
        self.save()

    class Meta:
        db_table = "clubs"
