from django.db import models
from django.utils.translation import gettext_lazy as _


class Position(models.TextChoices):
    ALUMNI = "ALUMNI", _("졸업생")
    MEMBER = "MEMBER", _("회원")
    STAFF = "STAFF", _("임원진")
    LEAD = "LEAD", _("부회장")
    OWNER = "OWNER", _("회장")
