import uuid

from django.contrib.postgres.fields import ArrayField
from django.db import models
from storages.backends.s3boto3 import S3Boto3Storage

from api.club.models import GenMember
from api.event.models.enums import AttendanceStatus
from api.event.models.event import Event


def event_image_path(instance, filename):
    # 파일 확장자 추출
    ext = filename.split(".")[-1]
    # UUID + 확장자로 새 파일명 생성
    filename = f"{uuid.uuid4()}.{ext}"
    return f"edit_requests/{filename}"


class EditRequest(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    gen_member = models.ForeignKey(GenMember, on_delete=models.CASCADE)
    reason = models.TextField(null=True, blank=True)
    images = ArrayField(
        models.ImageField(
            upload_to=event_image_path,
            storage=S3Boto3Storage(),
        ),
        blank=True,
        null=True,
        default=list,
    )
    status = models.IntegerField(
        choices=AttendanceStatus.choices,
        default=AttendanceStatus.PRESENT,
    )
    is_approved = models.BooleanField(default=False)
    is_rejected = models.BooleanField(default=False)
    approved_by = models.ForeignKey(
        GenMember,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_edit_requests",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_status_display(self):
        return AttendanceStatus(self.status).label

    def reject(self, gen_member: GenMember):
        self.is_rejected = True
        self.approved_by = gen_member
        self.save()

    def approve(self, gen_member: GenMember):
        self.is_approved = True
        self.approved_by = gen_member
        self.save()
