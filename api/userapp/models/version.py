from functools import total_ordering

from django.db import models

from api.userapp.models.user_meta import Platform
from config.abstract_models import TimeStampModel


@total_ordering
class Version(TimeStampModel):
    version = models.CharField(max_length=255)
    platform = models.CharField(max_length=255, choices=Platform.choices)
    required = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.platform} {self.version} {"필수" if self.required else "선택"}"

    def _version_tuple(self):
        """버전 문자열을 비교 가능한 튜플로 변환"""
        try:
            return tuple(map(int, self.version.split(".")))
        except ValueError:
            # 숫자가 아닌 경우 원본 문자열 반환
            return (self.version,)

    @staticmethod
    def transform_version(version: str):
        try:
            return tuple(map(int, version.split(".")))
        except ValueError:
            return (version,)

    def __eq__(self, other):
        if not isinstance(other, Version):
            return NotImplemented
        return self._version_tuple() == other._version_tuple()

    def __lt__(self, other):
        if not isinstance(other, Version):
            return NotImplemented
        return self._version_tuple() < other._version_tuple()

    def gt(self, version: str):
        """object가 입력보다 더 큰지"""
        return self._version_tuple() > self.transform_version(version)

    class Meta:
        db_table = "versions"
