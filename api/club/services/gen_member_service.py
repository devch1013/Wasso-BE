from api.club.models import GenMember, Role
from common.exceptions import CustomException, ErrorCode

from common.component import FCMComponent, NotificationTemplate
from api.club.models import Member
fcm_component = FCMComponent()

class GenMemberService:
    @staticmethod
    def update_gen_member(gen_member: GenMember, role_id: int):
        role = Role.objects.get(id=role_id)
        if gen_member.generation.club != role.club:
            raise CustomException(ErrorCode.ROLE_NOT_FOUND)
        if gen_member.role.is_superuser() and not gen_member.role == role:
            all_gen_members = GenMember.objects.filter(generation=gen_member.generation)
            superuser_count = 0
            for m in all_gen_members:
                if m.role.is_superuser():
                    superuser_count += 1
            if superuser_count <= 1:
                raise CustomException(ErrorCode.OWNER_ROLE_MUST_BE_MORE_THAN_ONE)
        gen_member.role = role
        gen_member.save()
        fcm_component.send_to_user(
            gen_member.member.user,
            NotificationTemplate.MEMBER_ROLE_CHANGE.get_title(),
            NotificationTemplate.MEMBER_ROLE_CHANGE.get_body(club_name=gen_member.generation.club.name, role_name=role.name),
        )

    @staticmethod
    def delete_gen_member(gen_member: GenMember):
        member = gen_member.member
        if gen_member.role.is_superuser():
            raise CustomException(ErrorCode.OWNER_CANNOT_BE_DELETED)
        gen_member.delete()
        if Member.objects.filter(generation=gen_member.generation).count() == 0:
            member.delete()
            