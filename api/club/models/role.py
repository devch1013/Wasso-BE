from django.db import models

from .club import Club


class Role(models.Model):
    def __str__(self):
        return f"{self.club.name} - {self.name}"

    name = models.CharField(max_length=255)
    club = models.ForeignKey(Club, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # 권한 관리
    role_manage = models.BooleanField(default=False)
    # 이벤트 관리
    event_manage = models.BooleanField(default=False)
    # 회원 관리 ,역할 수정
    member_manage = models.BooleanField(default=False)
    # 회원가입 수락
    signup_accept = models.BooleanField(default=False)
    # 학회 정보 수정
    club_info_manage = models.BooleanField(default=False)
    # 기수 변경 가능
    generation_change = models.BooleanField(default=False)
    # 출석 관리
    attendance_manage = models.BooleanField(default=False)
    # can edit history
    history_edit = models.BooleanField(default=False)

    @staticmethod
    def create_owner_role(club):
        role = Role()
        role.name = "회장"
        role.club = club
        role.role_manage = True
        role.event_manage = True
        role.member_manage = True
        role.signup_accept = True
        role.club_info_manage = True
        role.generation_change = True
        role.attendance_manage = True
        role.history_edit = True
        role.save()
        return role

    @staticmethod
    def create_admin_role(club):
        role = Role()
        role.name = "임원진"
        role.club = club
        role.role_manage = False
        role.event_manage = True
        role.member_manage = False
        role.signup_accept = True
        role.club_info_manage = False
        role.generation_change = False
        role.attendance_manage = True
        role.history_edit = False
        role.save()
        return role

    @staticmethod
    def create_member_role(club):
        role = Role()
        role.name = "회원"
        role.club = club
        role.role_manage = False
        role.event_manage = False
        role.member_manage = False
        role.signup_accept = False
        role.club_info_manage = False
        role.generation_change = False
        role.attendance_manage = False
        role.history_edit = False
        role.save()
        return role

    def is_superuser(self):
        return (
            self.role_manage
            and self.event_manage
            and self.member_manage
            and self.signup_accept
            and self.club_info_manage
            and self.generation_change
            and self.attendance_manage
            and self.history_edit
        )

    @staticmethod
    def get_highest_role(club: Club):
        return Role.objects.get(name="회장", club=club)
