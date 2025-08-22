from datetime import date, timedelta

import pytest
from django.urls import reverse
from rest_framework import status

from api.club.models import Generation
from api.event.models import Event


@pytest.mark.django_db
class TestGenerationApplyView:
    """기수 가입 신청 관련 테스트"""

    def test_generation_apply_success(
        self, authenticated_client, generation_with_apply
    ):
        """기수 가입 신청 목록 조회 성공 테스트"""
        generation, applies = generation_with_apply

        url = reverse("generations-apply", kwargs={"pk": generation.id})
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2  # 2개의 신청

    def test_generation_apply_empty(self, authenticated_client, club_with_member):
        """가입 신청이 없는 기수 테스트"""
        club, _ = club_with_member
        generation = club.current_generation

        url = reverse("generations-apply", kwargs={"pk": generation.id})
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 0

    def test_generation_apply_not_found(self, authenticated_client):
        """존재하지 않는 기수 신청 목록 조회 실패 테스트"""
        url = reverse("generations-apply", kwargs={"pk": 99999})
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_generation_apply_unauthorized(self, client, generation_with_apply):
        """인증되지 않은 사용자의 신청 목록 조회 실패 테스트"""
        generation, applies = generation_with_apply

        url = reverse("generations-apply", kwargs={"pk": generation.id})
        response = client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestGenerationMembersView:
    """기수 멤버 관련 테스트"""

    def test_generation_members_success(self, authenticated_client, club_with_members):
        """기수 멤버 목록 조회 성공 테스트"""
        club, members, gen_members = club_with_members
        generation = club.current_generation

        url = reverse("generations-members", kwargs={"pk": generation.id})
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 3  # 3명의 멤버

    def test_generation_members_ordering(self, authenticated_client, club_with_members):
        """기수 멤버 목록 정렬 테스트"""
        club, members, gen_members = club_with_members
        generation = club.current_generation

        url = reverse("generations-members", kwargs={"pk": generation.id})
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        # username 순으로 정렬되는지 확인
        usernames = [member["member"]["user"]["username"] for member in response.data]
        assert usernames == sorted(usernames)

    def test_generation_members_empty(
        self, authenticated_client, test_users, mock_storage
    ):
        """멤버가 없는 기수 테스트"""
        # user1 = test_users[0]
        generation = Generation.objects.create(
            club_id=1,  # 존재하지 않는 클럽
            name="빈기수",
            start_date=date.today(),
        )

        url = reverse("generations-members", kwargs={"pk": generation.id})
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 0

    def test_generation_members_not_found(self, authenticated_client):
        """존재하지 않는 기수 멤버 목록 조회 실패 테스트"""
        url = reverse("generations-members", kwargs={"pk": 99999})
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_generation_members_unauthorized(self, client, club_with_members):
        """인증되지 않은 사용자의 멤버 목록 조회 실패 테스트"""
        club, members, gen_members = club_with_members
        generation = club.current_generation

        url = reverse("generations-members", kwargs={"pk": generation.id})
        response = client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestGenerationEventsView:
    """기수 이벤트 관련 테스트"""

    def test_generation_events_success(self, authenticated_client, club_with_member):
        """기수 이벤트 목록 조회 성공 테스트"""
        club, _ = club_with_member
        generation = club.current_generation

        # 테스트 이벤트 생성
        Event.objects.create(
            name="테스트 이벤트1",
            date=date.today(),
            generation=generation,
        )
        Event.objects.create(
            name="테스트 이벤트2",
            date=date.today() + timedelta(days=1),
            generation=generation,
        )

        url = reverse("generations-events", kwargs={"pk": generation.id})
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2

    def test_generation_events_ordering(self, authenticated_client, club_with_member):
        """기수 이벤트 목록 정렬 테스트"""
        club, _ = club_with_member
        generation = club.current_generation

        # 날짜 순서가 다른 이벤트들 생성
        Event.objects.create(
            name="나중 이벤트",
            date=date.today() + timedelta(days=2),
            generation=generation,
        )
        Event.objects.create(
            name="먼저 이벤트",
            date=date.today(),
            generation=generation,
        )

        url = reverse("generations-events", kwargs={"pk": generation.id})
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        # 날짜 순으로 정렬되는지 확인
        event_names = [event["name"] for event in response.data]
        assert event_names == ["먼저 이벤트", "나중 이벤트"]

    def test_generation_events_empty(self, authenticated_client, club_with_member):
        """이벤트가 없는 기수 테스트"""
        club, _ = club_with_member
        generation = club.current_generation

        url = reverse("generations-events", kwargs={"pk": generation.id})
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 0

    def test_generation_events_not_found(self, authenticated_client):
        """존재하지 않는 기수 이벤트 목록 조회 실패 테스트"""
        url = reverse("generations-events", kwargs={"pk": 99999})
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_generation_events_unauthorized(self, client, club_with_member):
        """인증되지 않은 사용자의 이벤트 목록 조회 실패 테스트"""
        club, _ = club_with_member
        generation = club.current_generation

        url = reverse("generations-events", kwargs={"pk": generation.id})
        response = client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestGenerationStatsView:
    """기수 통계 관련 테스트"""

    def test_generation_stats_success(self, authenticated_client, club_with_members):
        """기수 통계 조회 성공 테스트"""
        club, members, gen_members = club_with_members
        generation = club.current_generation

        url = reverse("generations-stats", kwargs={"pk": generation.id})
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.data, list)

    def test_generation_stats_not_found(self, authenticated_client):
        """존재하지 않는 기수 통계 조회 실패 테스트"""
        url = reverse("generations-stats", kwargs={"pk": 99999})
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_generation_stats_unauthorized(self, client, club_with_members):
        """인증되지 않은 사용자의 통계 조회 실패 테스트"""
        club, members, gen_members = club_with_members
        generation = club.current_generation

        url = reverse("generations-stats", kwargs={"pk": generation.id})
        response = client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestGenerationActivateView:
    """기수 활성화 관련 테스트"""

    def test_generation_activate_success(
        self, authenticated_client, multiple_generations
    ):
        """기수 활성화 성공 테스트"""
        club, generations = multiple_generations
        inactive_generation = generations[0]  # 1기는 비활성화 상태

        url = reverse("generations-activate", kwargs={"pk": inactive_generation.id})
        response = authenticated_client.post(url)

        assert response.status_code == status.HTTP_200_OK

        # 활성화되었는지 확인
        inactive_generation.refresh_from_db()
        assert inactive_generation.activated is True

    def test_generation_activate_not_found(self, authenticated_client):
        """존재하지 않는 기수 활성화 실패 테스트"""
        url = reverse("generations-activate", kwargs={"pk": 99999})
        response = authenticated_client.post(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_generation_activate_unauthorized(self, client, multiple_generations):
        """인증되지 않은 사용자의 기수 활성화 실패 테스트"""
        club, generations = multiple_generations
        inactive_generation = generations[0]

        url = reverse("generations-activate", kwargs={"pk": inactive_generation.id})
        response = client.post(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestGenerationAutoApproveView:
    """기수 자동 승인 관련 테스트"""

    def test_generation_auto_approve_success(
        self, authenticated_client, club_with_member
    ):
        """기수 자동 승인 토글 성공 테스트"""
        club, _ = club_with_member
        generation = club.current_generation
        original_auto_approve = generation.auto_approve

        url = reverse("generations-auto-approve", kwargs={"pk": generation.id})
        response = authenticated_client.post(url)

        assert response.status_code == status.HTTP_200_OK

        # 자동 승인 설정이 토글되었는지 확인
        generation.refresh_from_db()
        assert generation.auto_approve != original_auto_approve

    def test_generation_auto_approve_not_found(self, authenticated_client):
        """존재하지 않는 기수 자동 승인 토글 실패 테스트"""
        url = reverse("generations-auto-approve", kwargs={"pk": 99999})
        response = authenticated_client.post(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_generation_auto_approve_unauthorized(self, client, club_with_member):
        """인증되지 않은 사용자의 자동 승인 토글 실패 테스트"""
        club, _ = club_with_member
        generation = club.current_generation

        url = reverse("generations-auto-approve", kwargs={"pk": generation.id})
        response = client.post(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestGenerationGoogleSheetView:
    """기수 구글 시트 관련 테스트"""

    def test_generation_google_sheet_success(
        self, authenticated_client, club_with_member, mock_google_sheet
    ):
        """기수 구글 시트 생성 성공 테스트"""
        club, _ = club_with_member
        generation = club.current_generation

        url = reverse("generations-google-sheet", kwargs={"pk": generation.id})
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert "url" in response.data
        assert "docs.google.com" in response.data["url"]

    def test_generation_google_sheet_not_found(
        self, authenticated_client, mock_google_sheet
    ):
        """존재하지 않는 기수 구글 시트 생성 실패 테스트"""
        url = reverse("generations-google-sheet", kwargs={"pk": 99999})
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_generation_google_sheet_unauthorized(
        self, client, club_with_member, mock_google_sheet
    ):
        """인증되지 않은 사용자의 구글 시트 생성 실패 테스트"""
        club, _ = club_with_member
        generation = club.current_generation

        url = reverse("generations-google-sheet", kwargs={"pk": generation.id})
        response = client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestGenerationNotionView:
    """기수 노션 연동 관련 테스트"""

    def test_generation_notion_get_success(
        self, authenticated_client, club_with_member
    ):
        """기수 노션 정보 조회 성공 테스트"""
        club, _ = club_with_member
        generation = club.current_generation

        # 노션 정보 설정
        club.notion_page_id = "test_page_id"
        club.notion_database_id = "test_database_id"
        club.save()

        url = reverse("generations-notion", kwargs={"pk": generation.id})
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["notion_page_id"] == "test_page_id"
        assert response.data["notion_database_id"] == "test_database_id"

    def test_generation_notion_post_success(
        self, authenticated_client, club_with_member
    ):
        """기수 노션 연동 성공 테스트"""
        club, _ = club_with_member
        generation = club.current_generation

        url = reverse("generations-notion", kwargs={"pk": generation.id})
        data = {"notion_database_url": "https://notion.so/database/test"}
        response = authenticated_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_202_ACCEPTED

    def test_generation_notion_post_invalid_data(
        self, authenticated_client, club_with_member
    ):
        """기수 노션 연동 유효하지 않은 데이터 테스트"""
        club, _ = club_with_member
        generation = club.current_generation

        url = reverse("generations-notion", kwargs={"pk": generation.id})
        data = {"notion_database_url": ""}  # 필수 필드 누락
        response = authenticated_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_generation_notion_not_found(self, authenticated_client):
        """존재하지 않는 기수 노션 연동 실패 테스트"""
        url = reverse("generations-notion", kwargs={"pk": 99999})
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_generation_notion_unauthorized(self, client, club_with_member):
        """인증되지 않은 사용자의 노션 연동 실패 테스트"""
        club, _ = club_with_member
        generation = club.current_generation

        url = reverse("generations-notion", kwargs={"pk": generation.id})
        response = client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestGenerationExcelView:
    """기수 엑셀 관련 테스트"""

    def test_generation_excel_success(
        self, authenticated_client, club_with_member, mock_excel
    ):
        """기수 엑셀 생성 성공 테스트"""
        club, _ = club_with_member
        generation = club.current_generation

        url = reverse("generations-excel", kwargs={"pk": generation.id})
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert "url" in response.data
        assert "attendance.xlsx" in response.data["url"]

    def test_generation_excel_not_found(self, authenticated_client, mock_excel):
        """존재하지 않는 기수 엑셀 생성 실패 테스트"""
        url = reverse("generations-excel", kwargs={"pk": 99999})
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_generation_excel_unauthorized(self, client, club_with_member, mock_excel):
        """인증되지 않은 사용자의 엑셀 생성 실패 테스트"""
        club, _ = club_with_member
        generation = club.current_generation

        url = reverse("generations-excel", kwargs={"pk": generation.id})
        response = client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestGenerationUpdateView:
    """기수 업데이트 관련 테스트"""

    def test_generation_update_success(self, authenticated_client, club_with_member):
        """기수 정보 업데이트 성공 테스트"""
        club, _ = club_with_member
        generation = club.current_generation

        url = reverse("generations-detail", kwargs={"pk": generation.id})
        data = {
            "name": "수정된기수",
            "start_date": "2024-02-01",
            "end_date": "2024-12-31",
        }
        response = authenticated_client.put(url, data, format="json")

        assert response.status_code == status.HTTP_200_OK

        # 정보가 업데이트되었는지 확인
        generation.refresh_from_db()
        assert generation.name == "수정된기수"

    def test_generation_update_invalid_data(
        self, authenticated_client, club_with_member
    ):
        """기수 정보 업데이트 유효하지 않은 데이터 테스트"""
        club, _ = club_with_member
        generation = club.current_generation

        url = reverse("generations-detail", kwargs={"pk": generation.id})
        data = {
            "name": "",  # 필수 필드 누락
            "start_date": "invalid-date",
        }
        response = authenticated_client.put(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_generation_update_not_found(self, authenticated_client):
        """존재하지 않는 기수 업데이트 실패 테스트"""
        url = reverse("generations-detail", kwargs={"pk": 99999})
        data = {"name": "새로운이름"}
        response = authenticated_client.put(url, data, format="json")

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_generation_update_unauthorized(self, client, club_with_member):
        """인증되지 않은 사용자의 기수 업데이트 실패 테스트"""
        club, _ = club_with_member
        generation = club.current_generation

        url = reverse("generations-detail", kwargs={"pk": generation.id})
        data = {"name": "새로운이름"}
        response = client.put(url, data, format="json")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestGenerationDeleteView:
    """기수 삭제 관련 테스트"""

    def test_generation_delete_success(self, authenticated_client, club_with_member):
        """기수 삭제 성공 테스트"""
        club, _ = club_with_member
        generation = club.current_generation

        url = reverse("generations-detail", kwargs={"pk": generation.id})
        response = authenticated_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT

        # 삭제되었는지 확인
        generation.refresh_from_db()
        assert generation.deleted is True
        assert generation.deleted_at is not None

    def test_generation_delete_not_found(self, authenticated_client):
        """존재하지 않는 기수 삭제 실패 테스트"""
        url = reverse("generations-detail", kwargs={"pk": 99999})
        response = authenticated_client.delete(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_generation_delete_unauthorized(self, client, club_with_member):
        """인증되지 않은 사용자의 기수 삭제 실패 테스트"""
        club, _ = club_with_member
        generation = club.current_generation

        url = reverse("generations-detail", kwargs={"pk": generation.id})
        response = client.delete(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestGenerationPermissions:
    """기수 권한 관련 테스트"""

    def test_permission_classes(self, client):
        """권한 클래스 테스트 - 인증되지 않은 사용자 접근 차단"""
        urls = [
            reverse("generations-detail", kwargs={"pk": 1}),
            reverse("generations-apply", kwargs={"pk": 1}),
            reverse("generations-members", kwargs={"pk": 1}),
            reverse("generations-events", kwargs={"pk": 1}),
            reverse("generations-stats", kwargs={"pk": 1}),
            reverse("generations-activate", kwargs={"pk": 1}),
            reverse("generations-auto-approve", kwargs={"pk": 1}),
            reverse("generations-google-sheet", kwargs={"pk": 1}),
            reverse("generations-notion", kwargs={"pk": 1}),
            reverse("generations-excel", kwargs={"pk": 1}),
        ]

        for url in urls:
            for method in ["get", "post", "put", "delete"]:
                if hasattr(client, method):
                    response = getattr(client, method)(url)
                    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_invalid_action_methods(self, authenticated_client, club_with_member):
        """잘못된 HTTP 메서드 사용 테스트"""
        club, _ = club_with_member
        generation_id = club.current_generation.id

        # apply는 GET만 지원
        url = reverse("generations-apply", kwargs={"pk": generation_id})
        response = authenticated_client.post(url, {})
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

        # activate는 POST만 지원
        url = reverse("generations-activate", kwargs={"pk": generation_id})
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

        # google-sheet는 GET만 지원
        url = reverse("generations-google-sheet", kwargs={"pk": generation_id})
        response = authenticated_client.post(url, {})
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

        # excel은 GET만 지원
        url = reverse("generations-excel", kwargs={"pk": generation_id})
        response = authenticated_client.post(url, {})
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED


@pytest.mark.django_db
class TestGenerationEdgeCases:
    """기수 엣지 케이스 테스트"""

    def test_deleted_generation_filtering(self, authenticated_client, club_with_member):
        """삭제된 기수 필터링 테스트"""
        club, _ = club_with_member
        generation = club.current_generation

        # 기수 삭제
        generation.delete()

        # 조회 시도
        url = reverse("generations-detail", kwargs={"pk": generation.id})
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_multiple_activations(self, authenticated_client, multiple_generations):
        """여러 기수 활성화 테스트"""
        club, generations = multiple_generations
        generation1, generation2 = generations

        # 1기 활성화
        url = reverse("generations-activate", kwargs={"pk": generation1.id})
        response = authenticated_client.post(url)
        assert response.status_code == status.HTTP_200_OK

        # 2기도 활성화 (동시에 여러 기수가 활성화될 수 있는지)
        url = reverse("generations-activate", kwargs={"pk": generation2.id})
        response = authenticated_client.post(url)
        assert response.status_code == status.HTTP_200_OK

    def test_auto_approve_toggle_multiple_times(
        self, authenticated_client, club_with_member
    ):
        """자동 승인 여러 번 토글 테스트"""
        club, _ = club_with_member
        generation = club.current_generation
        original_auto_approve = generation.auto_approve

        url = reverse("generations-auto-approve", kwargs={"pk": generation.id})

        # 첫 번째 토글
        response = authenticated_client.post(url)
        assert response.status_code == status.HTTP_200_OK

        # 두 번째 토글 (원래 상태로 돌아가야 함)
        response = authenticated_client.post(url)
        assert response.status_code == status.HTTP_200_OK

        generation.refresh_from_db()
        assert generation.auto_approve == original_auto_approve
