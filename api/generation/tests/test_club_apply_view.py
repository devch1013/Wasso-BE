from datetime import date

import pytest
from django.urls import reverse
from rest_framework import status

from api.club.models import ClubApply
from api.club.services.club_service import ClubService
from common.exceptions import ErrorCode


@pytest.mark.django_db
class TestClubApplyListView:
    """클럽 가입 신청 목록 관련 테스트"""

    def test_list_club_applies_success(
        self, authenticated_client, generation_with_apply
    ):
        """가입 신청 목록 조회 성공 테스트"""
        generation, applies = generation_with_apply

        url = reverse("club-apply-info")
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 0  # 인증된 사용자는 회장이므로 신청이 없음

    def test_list_my_applies(self, authenticated_client_2, generation_with_apply):
        """내 가입 신청 목록 조회 테스트"""
        generation, applies = generation_with_apply

        url = reverse("club-applies-list")
        response = authenticated_client_2.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1  # user2가 한 개의 신청이 있음

    def test_list_applies_empty(self, authenticated_client):
        """가입 신청이 없을 때 빈 목록 반환 테스트"""
        url = reverse("club-applies-list")
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 0

    def test_list_applies_unauthorized(self, client):
        """인증되지 않은 사용자의 가입 신청 목록 조회 실패 테스트"""
        url = reverse("club-applies-list")
        response = client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestClubApplyGetInfoView:
    """클럽 정보 조회 관련 테스트"""

    def test_get_info_success(self, authenticated_client, club_with_member):
        """클럽 코드로 정보 조회 성공 테스트"""
        club, _ = club_with_member

        url = reverse("club-apply-info")
        response = authenticated_client.get(
            url, {"code": club.current_generation.invite_code}
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == "1기"
        assert response.data["club"]["name"] == "테스트클럽"

    def test_get_info_missing_code(self, authenticated_client):
        """클럽 코드 누락 시 실패 테스트"""
        url = reverse("club-apply-info")
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert ErrorCode.PARAMS_MISSING.test_equal(response.data)

    def test_get_info_invalid_code(self, authenticated_client):
        """잘못된 클럽 코드로 조회 실패 테스트"""
        url = reverse("club-apply-info")
        response = authenticated_client.get(url, {"code": "invalid_code"})

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_info_unauthorized(self, client, club_with_member):
        """인증되지 않은 사용자의 클럽 정보 조회 실패 테스트"""
        club, _ = club_with_member

        url = reverse("club-apply-info")
        response = client.get(url, {"code": club.current_generation.invite_code})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestClubApplyActionView:
    """클럽 가입 신청 관련 테스트"""

    def test_apply_success(self, authenticated_client, test_users, mock_storage):
        """클럽 가입 신청 성공 테스트"""
        user1 = test_users[0]

        # 다른 사용자가 만든 클럽
        club, _ = ClubService.create_club(
            user=user1,
            name="신청할클럽",
            image=None,
            description="신청 테스트용",
            generation_data={"name": "1기", "start_date": date.today()},
        )

        # 다른 사용자로 인증
        url = reverse("club-apply")
        response = authenticated_client.post(
            url, {"club-code": club.current_generation.invite_code}
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert "successfully" in response.data["message"]

    def test_apply_missing_code(self, authenticated_client):
        """클럽 코드 누락 시 실패 테스트"""
        url = reverse("club-apply")
        response = authenticated_client.post(url)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert ErrorCode.PARAMS_MISSING.test_equal(response.data)

    def test_apply_invalid_code(self, authenticated_client):
        """잘못된 클럽 코드로 신청 실패 테스트"""
        url = reverse("club-apply")
        response = authenticated_client.post(url, {"club-code": "invalid_code"})

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_apply_duplicate(self, authenticated_client_2, generation_with_apply):
        """중복 신청 실패 테스트"""
        generation, applies = generation_with_apply

        url = reverse("club-apply")
        response = authenticated_client_2.post(
            url, {"club-code": generation.invite_code}
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_apply_unauthorized(self, client, club_with_member):
        """인증되지 않은 사용자의 가입 신청 실패 테스트"""
        club, _ = club_with_member

        url = reverse("club-apply")
        response = client.post(url, {"club-code": club.current_generation.invite_code})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestClubApplyApproveView:
    """클럽 가입 신청 승인 관련 테스트"""

    def test_approve_success(self, authenticated_client, generation_with_apply):
        """가입 신청 승인 성공 테스트"""
        generation, applies = generation_with_apply
        apply_id = applies[0].id

        url = reverse("club-apply-approve", kwargs={"apply_id": apply_id})
        response = authenticated_client.post(url)

        assert response.status_code == status.HTTP_200_OK
        assert "successfully" in response.data["message"]

        # 신청이 승인되었는지 확인
        apply_obj = ClubApply.objects.get(id=apply_id)
        assert apply_obj.accepted is True

    def test_approve_not_found(self, authenticated_client):
        """존재하지 않는 신청 승인 실패 테스트"""
        url = reverse("club-apply-approve", kwargs={"apply_id": 99999})
        response = authenticated_client.post(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_approve_unauthorized(self, client, generation_with_apply):
        """인증되지 않은 사용자의 신청 승인 실패 테스트"""
        generation, applies = generation_with_apply
        apply_id = applies[0].id

        url = reverse("club-apply-approve", kwargs={"apply_id": apply_id})
        response = client.post(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestClubApplyRejectView:
    """클럽 가입 신청 거부 관련 테스트"""

    def test_reject_success(self, authenticated_client, generation_with_apply):
        """가입 신청 거부 성공 테스트"""
        generation, applies = generation_with_apply
        apply_id = applies[0].id

        url = reverse("club-apply-reject", kwargs={"apply_id": apply_id})
        response = authenticated_client.post(url)

        assert response.status_code == status.HTTP_200_OK
        assert "successfully" in response.data["message"]

        # 신청이 거부되었는지 확인 (삭제됨)
        assert not ClubApply.objects.filter(id=apply_id).exists()

    def test_reject_not_found(self, authenticated_client):
        """존재하지 않는 신청 거부 실패 테스트"""
        url = reverse("club-apply-reject", kwargs={"apply_id": 99999})
        response = authenticated_client.post(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_reject_unauthorized(self, client, generation_with_apply):
        """인증되지 않은 사용자의 신청 거부 실패 테스트"""
        generation, applies = generation_with_apply
        apply_id = applies[0].id

        url = reverse("club-apply-reject", kwargs={"apply_id": apply_id})
        response = client.post(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestClubApplyNoticeTestView:
    """푸시 알림 테스트 관련 테스트"""

    def test_notice_test_success(self, authenticated_client, mock_fcm):
        """푸시 알림 테스트 성공 테스트"""
        url = reverse("club-apply-notice-test")
        response = authenticated_client.post(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["message"] == "success"

    def test_notice_test_unauthorized(self, client, mock_fcm):
        """인증되지 않은 사용자의 푸시 알림 테스트 실패 테스트"""
        url = reverse("club-apply-notice-test")
        response = client.post(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestClubApplyPermissions:
    """클럽 가입 신청 권한 관련 테스트"""

    def test_permission_classes(self, client):
        """권한 클래스 테스트 - 인증되지 않은 사용자 접근 차단"""
        urls = [
            reverse("club-applies-list"),
            reverse("club-apply-info"),
            reverse("club-apply"),
        ]

        for url in urls:
            response = client.get(url)
            assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_invalid_action_methods(self, authenticated_client):
        """잘못된 HTTP 메서드 사용 테스트"""
        # list는 GET만 지원
        url = reverse("club-applies-list")
        response = authenticated_client.post(url, {})
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

        # get_info는 GET만 지원
        url = reverse("club-apply-info")
        response = authenticated_client.post(url, {})
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
