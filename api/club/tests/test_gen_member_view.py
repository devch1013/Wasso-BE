import pytest
from django.urls import reverse
from rest_framework import status

from api.club.models import GenMember, Role


@pytest.mark.django_db
class TestGenMemberDestroyView:
    """기수 멤버 삭제 관련 테스트"""

    def test_destroy_gen_member_success(self, authenticated_client, club_with_members):
        """기수 멤버 삭제 성공 테스트"""
        club, members, gen_members = club_with_members
        gen_member_id = gen_members[1].id  # 두 번째 멤버 삭제

        url = reverse("gen-members-detail", kwargs={"pk": gen_member_id})
        response = authenticated_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT

        # 멤버가 삭제되었는지 확인
        gen_member = GenMember.objects.get(id=gen_member_id)
        assert gen_member.deleted is True
        assert gen_member.deleted_at is not None

    def test_destroy_gen_member_not_found(self, authenticated_client):
        """존재하지 않는 기수 멤버 삭제 실패 테스트"""
        url = reverse("gen-members-detail", kwargs={"pk": 99999})
        response = authenticated_client.delete(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_destroy_gen_member_unauthorized(self, client, club_with_members):
        """인증되지 않은 사용자의 기수 멤버 삭제 실패 테스트"""
        club, members, gen_members = club_with_members
        gen_member_id = gen_members[1].id

        url = reverse("gen-members-detail", kwargs={"pk": gen_member_id})
        response = client.delete(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestGenMemberRoleChangeView:
    """기수 멤버 역할 변경 관련 테스트"""

    def test_role_change_success(self, authenticated_client, club_with_members):
        """기수 멤버 역할 변경 성공 테스트"""
        club, members, gen_members = club_with_members
        gen_member = gen_members[1]  # 두 번째 멤버의 역할 변경
        executive_role = Role.objects.get(club=club, name="임원진")

        url = reverse("gen-members-role-change", kwargs={"pk": gen_member.id})
        data = {"role_id": executive_role.id}
        response = authenticated_client.put(url, data, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert "완료" in response.data["message"]

        # 역할이 변경되었는지 확인
        gen_member.refresh_from_db()
        assert gen_member.role == executive_role

    def test_role_change_invalid_data(self, authenticated_client, club_with_members):
        """기수 멤버 역할 변경 유효하지 않은 데이터 테스트"""
        club, members, gen_members = club_with_members
        gen_member = gen_members[1]

        url = reverse("gen-members-role-change", kwargs={"pk": gen_member.id})
        data = {"role_id": ""}  # 필수 필드 누락
        response = authenticated_client.put(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_role_change_not_found_member(self, authenticated_client):
        """존재하지 않는 기수 멤버 역할 변경 실패 테스트"""
        url = reverse("gen-members-role-change", kwargs={"pk": 99999})
        data = {"role_id": 1}
        response = authenticated_client.put(url, data, format="json")

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_role_change_not_found_role(self, authenticated_client, club_with_members):
        """존재하지 않는 역할로 변경 실패 테스트"""
        club, members, gen_members = club_with_members
        gen_member = gen_members[1]

        url = reverse("gen-members-role-change", kwargs={"pk": gen_member.id})
        data = {"role_id": 99999}  # 존재하지 않는 역할
        response = authenticated_client.put(url, data, format="json")

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_role_change_unauthorized(self, client, club_with_members):
        """인증되지 않은 사용자의 역할 변경 실패 테스트"""
        club, members, gen_members = club_with_members
        gen_member = gen_members[1]
        executive_role = Role.objects.get(club=club, name="임원진")

        url = reverse("gen-members-role-change", kwargs={"pk": gen_member.id})
        data = {"role_id": executive_role.id}
        response = client.put(url, data, format="json")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestGenMemberAttendancesView:
    """기수 멤버 출석 조회 관련 테스트"""

    def test_attendances_success(self, authenticated_client, club_with_members):
        """기수 멤버 출석 조회 성공 테스트"""
        club, members, gen_members = club_with_members
        gen_member = gen_members[0]

        url = reverse("gen-members-attendances", kwargs={"pk": gen_member.id})
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.data, list)

    def test_attendances_not_found(self, authenticated_client):
        """존재하지 않는 기수 멤버 출석 조회 실패 테스트"""
        url = reverse("gen-members-attendances", kwargs={"pk": 99999})
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_attendances_unauthorized(self, client, club_with_members):
        """인증되지 않은 사용자의 출석 조회 실패 테스트"""
        club, members, gen_members = club_with_members
        gen_member = gen_members[0]

        url = reverse("gen-members-attendances", kwargs={"pk": gen_member.id})
        response = client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestGenMemberPermissions:
    """기수 멤버 권한 관련 테스트"""

    def test_permission_classes(self, client):
        """권한 클래스 테스트 - 인증되지 않은 사용자 접근 차단"""
        urls = [
            reverse("gen-members-detail", kwargs={"pk": 1}),
            reverse("gen-members-role-change", kwargs={"pk": 1}),
            reverse("gen-members-attendances", kwargs={"pk": 1}),
        ]

        for url in urls:
            for method in ["get", "put", "delete"]:
                if hasattr(client, method):
                    response = getattr(client, method)(url)
                    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_invalid_action_methods(self, authenticated_client, club_with_members):
        """잘못된 HTTP 메서드 사용 테스트"""
        club, members, gen_members = club_with_members
        gen_member_id = gen_members[0].id

        # role_change는 PUT만 지원
        url = reverse("gen-members-role-change", kwargs={"pk": gen_member_id})
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

        # attendances는 GET만 지원
        url = reverse("gen-members-attendances", kwargs={"pk": gen_member_id})
        response = authenticated_client.post(url, {})
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_queryset_filtering(self, authenticated_client, club_with_members):
        """queryset 필터링 테스트"""
        club, members, gen_members = club_with_members

        # 모든 기수 멤버가 조회 가능한지 확인
        for gen_member in gen_members:
            url = reverse("gen-members-detail", kwargs={"pk": gen_member.id})
            response = authenticated_client.get(url)
            # GET이 지원되지 않으므로 405 에러가 나와야 함
            assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED


@pytest.mark.django_db
class TestGenMemberEdgeCases:
    """기수 멤버 엣지 케이스 테스트"""

    def test_role_change_to_same_role(self, authenticated_client, club_with_members):
        """같은 역할로 변경 시도 테스트"""
        club, members, gen_members = club_with_members
        gen_member = gen_members[1]
        current_role = gen_member.role

        url = reverse("gen-members-role-change", kwargs={"pk": gen_member.id})
        data = {"role_id": current_role.id}
        response = authenticated_client.put(url, data, format="json")

        assert response.status_code == status.HTTP_200_OK
        # 역할이 그대로 유지되는지 확인
        gen_member.refresh_from_db()
        assert gen_member.role == current_role

    def test_destroy_already_deleted_member(
        self, authenticated_client, club_with_members
    ):
        """이미 삭제된 멤버 재삭제 시도 테스트"""
        club, members, gen_members = club_with_members
        gen_member = gen_members[1]

        # 먼저 삭제
        url = reverse("gen-members-detail", kwargs={"pk": gen_member.id})
        response = authenticated_client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT

        # 다시 삭제 시도
        response = authenticated_client.delete(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_role_change_deleted_member(self, authenticated_client, club_with_members):
        """삭제된 멤버의 역할 변경 시도 테스트"""
        club, members, gen_members = club_with_members
        gen_member = gen_members[1]
        executive_role = Role.objects.get(club=club, name="임원진")

        # 먼저 삭제
        url = reverse("gen-members-detail", kwargs={"pk": gen_member.id})
        authenticated_client.delete(url)

        # 삭제된 멤버의 역할 변경 시도
        url = reverse("gen-members-role-change", kwargs={"pk": gen_member.id})
        data = {"role_id": executive_role.id}
        response = authenticated_client.put(url, data, format="json")

        assert response.status_code == status.HTTP_404_NOT_FOUND
