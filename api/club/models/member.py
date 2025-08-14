import uuid

from django.contrib.postgres.fields import ArrayField
from django.db import models
from storages.backends.s3boto3 import S3Boto3Storage

from api.club.models.club import Club
from api.userapp.models import User
from config.abstract_models.soft_delete_model import SoftDeleteModel


def member_profile_image_path(instance, filename):
    # 파일 확장자 추출
    ext = filename.split(".")[-1]
    # UUID + 확장자로 새 파일명 생성
    filename = f"{uuid.uuid4()}.{ext}"
    return f"member_profile/{filename}"


class Member(SoftDeleteModel):
    def __str__(self):
        return f"{self.user.username} - {self.club.name}"

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name="members")
    short_description = models.TextField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    tags = ArrayField(
        models.CharField(max_length=100), blank=True, null=True, default=list
    )
    profile_image = models.ImageField(
        upload_to=member_profile_image_path,
        storage=S3Boto3Storage(),
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_current_generation(self):
        return self.gen_members.filter(is_current=True).first()

    class Meta:
        db_table = "member"
