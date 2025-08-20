from datetime import date, timedelta

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from api.club.models import ClubApply, Generation
from api.club.services.club_service import ClubService
from api.club.tests.club_test_utils import ClubTestUtils
from common.exceptions import ErrorCode
from common.test_utils.image_utils import ImageTestUtils


@pytest.fixture
def test_users():
    """테스트용 사용자들 생성"""
    return ClubTestUtils.get_test_users(count=3)


@pytest.fixture
def client():
    """인증되지 않은 API 클라이언트"""
    return APIClient()


@pytest.fixture
def authenticated_client(test_users):
    """인증된 API 클라이언트"""
    client = APIClient()
    user1 = test_users[0]
    client.force_authenticate(user=user1)
    return client


@pytest.fixture
def test_image():
    """테스트용 이미지"""
    return ImageTestUtils.create_test_image()


@pytest.fixture
def large_test_image():
    """큰 테스트용 이미지"""
    return ImageTestUtils.create_test_image(width=2000, height=2000)


@pytest.fixture
def mock_storage(mocker):
    """S3 저장소 모킹"""
    return mocker.patch(
        "django.core.files.storage.default_storage.save",
        return_value="test-image-path.jpg",
    )


@pytest.fixture
def club_with_member(test_users, mock_storage):
    """클럽과 멤버가 생성된 fixture"""
    user1 = test_users[0]
    club, member = ClubService.create_club(
        user=user1,
        name="테스트클럽",
        image=None,
        description="테스트 클럽 설명",
        generation_data={
            "name": "1기",
            "start_date": date.today(),
            "end_date": date.today() + timedelta(days=365),
        },
    )
    return club, member


@pytest.mark.django_db
class TestClubListView:
    """클럽 목록 관련 테스트"""

    def test_list_clubs_success(
        self, authenticated_client, test_users, test_image, mock_storage
    ):
        """클럽 목록 조회 성공 테스트"""
        user1 = test_users[0]

        # 클럽 2개 생성
        club1, _ = ClubService.create_club(
            user=user1,
            name="테스트클럽1",
            image=test_image,
            description="테스트 클럽 1 설명",
            generation_data={
                "name": "1기",
                "start_date": date.today(),
                "end_date": date.today() + timedelta(days=365),
            },
        )

        club2, _ = ClubService.create_club(
            user=user1,
            name="테스트클럽2",
            image=None,
            description="테스트 클럽 2 설명",
            generation_data={
                "name": "1기",
                "start_date": date.today(),
                "end_date": date.today() + timedelta(days=365),
            },
        )

        url = reverse("clubs-list")
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2

        # 클럽 이름 순으로 정렬되는지 확인
        club_names = [item["club_name"] for item in response.data]
        assert club_names == ["테스트클럽1", "테스트클럽2"]

    def test_list_clubs_empty(self, authenticated_client):
        """클럽이 없을 때 빈 목록 반환 테스트"""
        url = reverse("clubs-list")
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 0

    def test_list_clubs_with_deleted_club(
        self, authenticated_client, test_users, mock_storage
    ):
        """삭제된 클럽은 목록에 나오지 않는 테스트"""
        user1 = test_users[0]

        club, _ = ClubService.create_club(
            user=user1,
            name="삭제될클럽",
            image=None,
            description="삭제될 클럽",
            generation_data={
                "name": "1기",
                "start_date": date.today(),
            },
        )

        # 클럽 삭제
        club.delete()

        url = reverse("clubs-list")
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 0

    def test_list_clubs_unauthorized(self, client):
        """인증되지 않은 사용자의 클럽 목록 조회 실패 테스트"""
        url = reverse("clubs-list")
        response = client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_queryset_only_user_clubs(self, client, test_users, mock_storage):
        """사용자가 속한 클럽만 조회되는지 테스트"""
        user1, user2 = test_users[0], test_users[1]

        # user1의 클럽 생성
        club1, _ = ClubService.create_club(
            user=user1,
            name="유저1클럽",
            image=None,
            description="유저1만의 클럽",
            generation_data={"name": "1기", "start_date": date.today()},
        )

        # user2의 클럽 생성 (user1은 멤버가 아님)
        client.force_authenticate(user=user2)
        club2, _ = ClubService.create_club(
            user=user2,
            name="유저2클럽",
            image=None,
            description="유저2만의 클럽",
            generation_data={"name": "1기", "start_date": date.today()},
        )

        # user1으로 다시 인증하고 목록 조회
        client.force_authenticate(user=user1)
        url = reverse("clubs-list")
        response = client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["club_name"] == "유저1클럽"


@pytest.mark.django_db
class TestClubDetailView:
    """클럽 상세 관련 테스트"""

    def test_retrieve_club_success(
        self, authenticated_client, test_users, test_image, mock_storage
    ):
        """클럽 상세 조회 성공 테스트"""
        user1 = test_users[0]

        club, _ = ClubService.create_club(
            user=user1,
            name="상세조회테스트클럽",
            image=test_image,
            description="상세 조회용 클럽",
            generation_data={
                "name": "1기",
                "start_date": date.today(),
                "end_date": date.today() + timedelta(days=365),
            },
        )

        url = reverse("clubs-detail", kwargs={"pk": club.id})
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == "상세조회테스트클럽"
        assert response.data["description"] == "상세 조회용 클럽"
        assert response.data["current_generation"] is not None
        assert response.data["my_role"] == "회장"

    def test_retrieve_club_not_found(self, authenticated_client):
        """존재하지 않는 클럽 조회 실패 테스트"""
        url = reverse("clubs-detail", kwargs={"pk": 99999})
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_retrieve_deleted_club(
        self, authenticated_client, test_users, mock_storage
    ):
        """삭제된 클럽 조회 실패 테스트"""
        user1 = test_users[0]

        club, _ = ClubService.create_club(
            user=user1,
            name="삭제된클럽",
            image=None,
            description="삭제된 클럽",
            generation_data={"name": "1기", "start_date": date.today()},
        )

        club.delete()

        url = reverse("clubs-detail", kwargs={"pk": club.id})
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_object_deleted_club_handling(
        self, authenticated_client, test_users, mock_storage
    ):
        """get_object에서 삭제된 클럽 처리 테스트"""
        user1 = test_users[0]

        club, _ = ClubService.create_club(
            user=user1,
            name="삭제될클럽2",
            image=None,
            description="삭제될 클럽",
            generation_data={"name": "1기", "start_date": date.today()},
        )

        # 클럽 삭제
        club.delete()

        # retrieve 호출
        url = reverse("clubs-detail", kwargs={"pk": club.id})
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_serializer_context_passing(
        self, authenticated_client, test_users, mock_storage
    ):
        """serializer에 request context가 올바르게 전달되는지 테스트"""
        user1 = test_users[0]

        club, _ = ClubService.create_club(
            user=user1,
            name="컨텍스트테스트클럽",
            image=None,
            description="컨텍스트 테스트용",
            generation_data={"name": "1기", "start_date": date.today()},
        )

        url = reverse("clubs-detail", kwargs={"pk": club.id})
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        # my_role 필드가 올바르게 설정되었는지 확인 (이는 request context를 사용함)
        assert response.data["my_role"] == "회장"


@pytest.mark.django_db
class TestClubCreateView:
    """클럽 생성 관련 테스트"""

    def test_create_club_success(self, authenticated_client, test_users, mock_storage):
        """클럽 생성 성공 테스트"""
        url = reverse("clubs-list")
        data = {
            "name": "새로운클럽",
            "description": "새로운 클럽 설명",
            "generation": {
                "name": "1기",
                "start_date": "2024-01-01",
                "end_date": "2024-12-31",
            },
        }

        response = authenticated_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["club_name"] == "새로운클럽"

    def test_create_club_invalid_data(self, authenticated_client):
        """클럽 생성 유효하지 않은 데이터 테스트"""
        url = reverse("clubs-list")
        data = {
            "name": "",  # 필수 필드 누락
            "generation": {
                "name": "1기",
                "start_date": "2024-01-01",
            },
        }

        response = authenticated_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_club_missing_generation(self, authenticated_client):
        """클럽 생성 시 기수 정보 누락 테스트"""
        url = reverse("clubs-list")
        data = {
            "name": "테스트클럽",
            "description": "테스트 설명",
        }

        response = authenticated_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_club_duplicate_name(self, authenticated_client, mock_storage):
        """중복된 클럽명으로 생성 실패 테스트"""
        url = reverse("clubs-list")
        data = {
            "name": "중복클럽",
            "description": "중복된 클럽명",
            "generation": {
                "name": "1기",
                "start_date": "2024-01-01",
            },
        }

        response = authenticated_client.post(url, data, format="json")
        assert response.status_code == status.HTTP_201_CREATED

        response = authenticated_client.post(url, data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert ErrorCode.CLUB_ALREADY_EXISTS.test_equal(response.data)

    def test_large_image_handling(
        self, authenticated_client, large_test_image, mock_storage
    ):
        """큰 이미지 파일 처리 테스트"""
        mock_storage.return_value = "large-test-image-path.jpg"

        url = reverse("clubs-list")
        data = {
            "name": "큰이미지클럽",
            "image": large_test_image,
            "description": "큰 이미지 테스트",
            "generation.name": "1기",
            "generation.start_date": "2024-01-01",
        }

        response = authenticated_client.post(url, data, format="multipart")

        # 성공적으로 처리되어야 함 (S3 mock이 처리)
        assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
class TestClubUpdateView:
    """클럽 수정 관련 테스트"""

    def test_update_club_success(self, authenticated_client, test_users, mock_storage):
        """클럽 정보 수정 성공 테스트"""
        user1 = test_users[0]

        club, _ = ClubService.create_club(
            user=user1,
            name="수정전클럽",
            image=None,
            description="수정 전 설명",
            generation_data={"name": "1기", "start_date": date.today()},
        )

        url = reverse("clubs-detail", kwargs={"pk": club.id})
        data = {
            "name": "수정후클럽",
            "description": "수정 후 설명",
        }

        response = authenticated_client.put(url, data, format="json")

        assert response.status_code == status.HTTP_200_OK
        club.refresh_from_db()
        assert club.name == "수정후클럽"
        assert club.description == "수정 후 설명"

    def test_update_club_not_found(self, authenticated_client):
        """존재하지 않는 클럽 수정 실패 테스트"""
        url = reverse("clubs-detail", kwargs={"pk": 99999})
        data = {"name": "수정된이름"}

        response = authenticated_client.put(url, data, format="json")

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_club_partial(self, authenticated_client, test_users, mock_storage):
        """클럽 부분 수정 테스트"""
        user1 = test_users[0]

        club, _ = ClubService.create_club(
            user=user1,
            name="부분수정클럽",
            image=None,
            description="원래 설명",
            generation_data={"name": "1기", "start_date": date.today()},
        )

        url = reverse("clubs-detail", kwargs={"pk": club.id})
        data = {"name": "부분수정완료클럽"}  # description은 수정하지 않음

        response = authenticated_client.put(url, data, format="json")

        assert response.status_code == status.HTTP_200_OK
        club.refresh_from_db()
        assert club.name == "부분수정완료클럽"
        assert club.description == "원래 설명"  # 변경되지 않음


@pytest.mark.django_db
class TestClubDeleteView:
    """클럽 삭제 관련 테스트"""

    def test_destroy_club_success(self, authenticated_client, test_users, mock_storage):
        """클럽 삭제 성공 테스트"""
        user1 = test_users[0]

        club, _ = ClubService.create_club(
            user=user1,
            name="삭제할클럽",
            image=None,
            description="삭제할 클럽",
            generation_data={"name": "1기", "start_date": date.today()},
        )

        url = reverse("clubs-detail", kwargs={"pk": club.id})
        response = authenticated_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        club.refresh_from_db()
        assert club.deleted is True
        assert club.deleted_at is not None

    def test_destroy_club_not_found(self, authenticated_client):
        """존재하지 않는 클럽 삭제 실패 테스트"""
        url = reverse("clubs-detail", kwargs={"pk": 99999})
        response = authenticated_client.delete(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestClubAppliesView:
    """클럽 가입 신청 관련 테스트"""

    def test_applies_action_success(
        self, authenticated_client, test_users, mock_storage
    ):
        """클럽 가입 신청 목록 조회 성공 테스트"""
        user1, user2, user3 = test_users

        club, _ = ClubService.create_club(
            user=user1,
            name="신청테스트클럽",
            image=None,
            description="가입 신청 테스트용",
            generation_data={"name": "1기", "start_date": date.today()},
        )

        # 가입 신청 생성
        ClubApply.objects.create(user=user2, generation=club.current_generation)
        ClubApply.objects.create(user=user3, generation=club.current_generation)

        url = reverse("clubs-applies", kwargs={"pk": club.current_generation.id})
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2

    def test_applies_action_empty(self, authenticated_client, test_users, mock_storage):
        """가입 신청이 없는 경우 테스트"""
        user1 = test_users[0]

        club, _ = ClubService.create_club(
            user=user1,
            name="신청없는클럽",
            image=None,
            description="가입 신청이 없는 클럽",
            generation_data={"name": "1기", "start_date": date.today()},
        )

        url = reverse("clubs-applies", kwargs={"pk": club.current_generation.id})
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 0


@pytest.mark.django_db
class TestClubRolesView:
    """클럽 역할 관련 테스트"""

    def test_roles_action_success(self, authenticated_client, test_users, mock_storage):
        """클럽 역할 목록 조회 성공 테스트"""
        user1 = test_users[0]

        club, _ = ClubService.create_club(
            user=user1,
            name="역할테스트클럽",
            image=None,
            description="역할 테스트용",
            generation_data={"name": "1기", "start_date": date.today()},
        )

        url = reverse("clubs-roles", kwargs={"pk": club.id})
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 3  # 회장, 임원진, 회원

        # 기본 역할들이 모두 생성되었는지 확인
        role_names = [role["name"] for role in response.data]
        assert "회장" in role_names
        assert "임원진" in role_names
        assert "회원" in role_names


@pytest.mark.django_db
class TestClubGenerationsView:
    """클럽 기수 관련 테스트"""

    def test_generations_get_success(
        self, authenticated_client, test_users, mock_storage
    ):
        """클럽 기수 목록 조회 성공 테스트"""
        user1 = test_users[0]

        club, _ = ClubService.create_club(
            user=user1,
            name="기수테스트클럽",
            image=None,
            description="기수 테스트용",
            generation_data={"name": "1기", "start_date": date.today()},
        )

        # 추가 기수 생성
        Generation.objects.create(
            club=club,
            name="2기",
            start_date=date.today() + timedelta(days=365),
            activated=False,
        )

        url = reverse("clubs-generations", kwargs={"pk": club.id})
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2

        # start_date 순으로 정렬되는지 확인
        generation_names = [gen["name"] for gen in response.data]
        assert generation_names == ["1기", "2기"]

    def test_generations_post_success(
        self, authenticated_client, test_users, mock_storage
    ):
        """클럽 기수 생성 성공 테스트"""
        user1 = test_users[0]

        club, _ = ClubService.create_club(
            user=user1,
            name="기수생성테스트클럽",
            image=None,
            description="기수 생성 테스트용",
            generation_data={"name": "1기", "start_date": date.today()},
        )

        url = reverse("clubs-generations", kwargs={"pk": club.id})
        data = {
            "name": "2기",
            "start_date": "2024-12-01",
            "end_date": "2025-11-30",
        }
        print(url)
        response = authenticated_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["name"] == "2기"

    def test_generations_post_invalid_data(
        self, authenticated_client, test_users, mock_storage
    ):
        """클럽 기수 생성 유효하지 않은 데이터 테스트"""
        user1 = test_users[0]

        club, _ = ClubService.create_club(
            user=user1,
            name="기수생성실패테스트클럽",
            image=None,
            description="기수 생성 실패 테스트용",
            generation_data={"name": "1기", "start_date": date.today()},
        )

        url = reverse("clubs-generations", kwargs={"pk": club.id})
        data = {
            "name": "",  # 필수 필드 누락
            "start_date": "invalid-date",  # 잘못된 날짜 형식
        }

        response = authenticated_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_generations_with_deleted_generations(
        self, authenticated_client, test_users, mock_storage
    ):
        """삭제된 기수는 목록에 나오지 않는 테스트"""
        user1 = test_users[0]

        club, _ = ClubService.create_club(
            user=user1,
            name="기수삭제테스트클럽",
            image=None,
            description="기수 삭제 테스트용",
            generation_data={"name": "1기", "start_date": date.today()},
        )

        # 추가 기수 생성 후 삭제
        generation2 = Generation.objects.create(
            club=club,
            name="2기",
            start_date=date.today() + timedelta(days=365),
        )
        generation2.delete()

        url = reverse("clubs-generations", kwargs={"pk": club.id})
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1  # 삭제된 기수 제외

    def test_edge_case_multiple_generations(
        self, authenticated_client, test_users, mock_storage
    ):
        """여러 기수가 있는 클럽에서의 동작 테스트"""
        user1 = test_users[0]

        club, _ = ClubService.create_club(
            user=user1,
            name="다기수클럽",
            image=None,
            description="여러 기수 테스트용",
            generation_data={
                "name": "1기",
                "start_date": date.today() - timedelta(days=365),
            },
        )

        # 현재 기수로 2기 생성
        generation2 = Generation.objects.create(
            club=club,
            name="2기",
            start_date=date.today(),
            end_date=date.today() + timedelta(days=365),
            activated=True,
        )

        # current_generation 업데이트
        club.current_generation = generation2
        club.save()

        url = reverse("clubs-detail", kwargs={"pk": club.id})
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["current_generation"]["name"] == "2기"


@pytest.mark.django_db
class TestClubPermissions:
    """클럽 권한 관련 테스트"""

    def test_permission_classes(self, client):
        """권한 클래스 테스트 - 인증되지 않은 사용자 접근 차단"""
        urls = [
            reverse("clubs-list"),
            reverse("clubs-detail", kwargs={"pk": 1}),
        ]

        for url in urls:
            for method in ["get", "post", "put", "patch", "delete"]:
                if hasattr(client, method):
                    response = getattr(client, method)(url)
                    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_invalid_action_methods(self, authenticated_client):
        """잘못된 HTTP 메서드 사용 테스트"""
        # applies 액션은 GET만 지원
        url = reverse("clubs-applies", kwargs={"pk": 1})
        response = authenticated_client.post(url, {})
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

        # roles 액션은 GET만 지원
        url = reverse("clubs-roles", kwargs={"pk": 1})
        response = authenticated_client.put(url, {})
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
