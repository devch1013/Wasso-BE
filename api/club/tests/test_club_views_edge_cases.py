from datetime import date, timedelta
from unittest.mock import Mock, patch

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from api.club.services.club_service import ClubService
from api.generation.models import ClubApply, Generation, GenMember
from api.userapp.enums import Provider
from api.userapp.models import User
from common.test_utils.image_utils import ImageTestUtils


class ClubViewSetEdgeCasesTestCase(APITestCase):
    """ClubViewSet의 엣지 케이스 및 상세 시나리오 테스트"""

    @patch("django.core.files.storage.default_storage.save")
    def setUp(self, mock_storage):
        """테스트 환경 설정"""
        mock_storage.return_value = "test-image-path.jpg"

        # 테스트용 사용자들 생성
        self.owner_user = User.objects.create_user(
            identifier="owner123",
            username="클럽소유자",
            email="owner@example.com",
            provider=Provider.KAKAO,
            initialized=True,
        )
        self.admin_user = User.objects.create_user(
            identifier="admin123",
            username="클럽관리자",
            email="admin@example.com",
            provider=Provider.KAKAO,
            initialized=True,
        )
        self.member_user = User.objects.create_user(
            identifier="member123",
            username="일반회원",
            email="member@example.com",
            provider=Provider.KAKAO,
            initialized=True,
        )
        self.outsider_user = User.objects.create_user(
            identifier="outsider123",
            username="외부인",
            email="outsider@example.com",
            provider=Provider.KAKAO,
            initialized=True,
        )

        # API 클라이언트 설정
        self.client = APIClient()

    @patch("django.core.files.storage.default_storage.save")
    def test_club_member_permissions(self, mock_storage):
        """클럽 멤버별 권한 테스트"""
        mock_storage.return_value = "test-image-path.jpg"

        # 클럽 생성 (owner_user가 소유자)
        club, owner_member = ClubService.create_club(
            user=self.owner_user,
            name="권한테스트클럽",
            image=None,
            description="권한 테스트용 클럽",
            generation_data={
                "name": "1기",
                "start_date": date.today(),
                "end_date": date.today() + timedelta(days=365),
            },
        )

        # 다른 사용자들을 클럽에 추가
        from api.club.models import Member, Role

        # 관리자 추가
        admin_member = Member.objects.create(user=self.admin_user, club=club)
        admin_role = Role.objects.filter(club=club, name="임원진").first()
        GenMember.objects.create(
            member=admin_member,
            generation=club.current_generation,
            role=admin_role,
            is_current=True,
        )

        # 일반 회원 추가
        member_member = Member.objects.create(user=self.member_user, club=club)
        member_role = Role.objects.filter(club=club, name="회원").first()
        GenMember.objects.create(
            member=member_member,
            generation=club.current_generation,
            role=member_role,
            is_current=True,
        )

        # 1. 소유자 권한 테스트 - 클럽 수정 가능
        self.client.force_authenticate(user=self.owner_user)
        url = reverse("clubs-detail", kwargs={"pk": club.id})
        data = {"name": "수정된클럽명"}
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 2. 관리자 권한 테스트 - roles 조회 가능
        self.client.force_authenticate(user=self.admin_user)
        url = reverse("clubs-roles", kwargs={"pk": club.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 3. 일반 회원 권한 테스트 - 클럽 조회만 가능
        self.client.force_authenticate(user=self.member_user)
        url = reverse("clubs-detail", kwargs={"pk": club.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 4. 외부인 권한 테스트 - 클럽 조회 불가
        self.client.force_authenticate(user=self.outsider_user)
        url = reverse("clubs-detail", kwargs={"pk": club.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    @patch("django.core.files.storage.default_storage.save")
    def test_multiple_generations_handling(self, mock_storage):
        """여러 기수 처리 테스트"""
        mock_storage.return_value = "test-image-path.jpg"

        club, member = ClubService.create_club(
            user=self.owner_user,
            name="다기수클럽",
            image=None,
            description="여러 기수 테스트",
            generation_data={
                "name": "1기",
                "start_date": date.today() - timedelta(days=365),
            },
        )

        # 2기 생성
        generation2 = Generation.objects.create(
            club=club,
            name="2기",
            start_date=date.today() - timedelta(days=180),
            end_date=date.today() + timedelta(days=180),
            activated=True,
        )

        # 3기 생성 (미래)
        Generation.objects.create(
            club=club,
            name="3기",
            start_date=date.today() + timedelta(days=180),
            end_date=date.today() + timedelta(days=545),
            activated=False,
        )

        # current_generation을 2기로 변경
        club.current_generation = generation2
        club.save()

        self.client.force_authenticate(user=self.owner_user)

        # 기수 목록 조회 테스트
        url = reverse("clubs-generations", kwargs={"pk": club.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

        # start_date 순으로 정렬되는지 확인
        generation_names = [gen["name"] for gen in response.data]
        self.assertEqual(generation_names, ["1기", "2기", "3기"])

        # 클럽 상세에서 current_generation 확인
        url = reverse("clubs-detail", kwargs={"pk": club.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["current_generation"]["name"], "2기")

    @patch("django.core.files.storage.default_storage.save")
    def test_club_soft_delete_behavior(self, mock_storage):
        """클럽 소프트 삭제 동작 테스트"""
        mock_storage.return_value = "test-image-path.jpg"

        club, member = ClubService.create_club(
            user=self.owner_user,
            name="삭제테스트클럽",
            image=None,
            description="삭제 테스트용",
            generation_data={"name": "1기", "start_date": date.today()},
        )

        self.client.force_authenticate(user=self.owner_user)

        # 삭제 전 - 정상 조회 가능
        url = reverse("clubs-detail", kwargs={"pk": club.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 클럽 삭제
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # 삭제 후 - 조회 불가
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # 목록에서도 제외됨
        url = reverse("clubs-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

        # DB에서는 삭제되지 않고 deleted=True로 설정됨
        club.refresh_from_db()
        self.assertTrue(club.deleted)
        self.assertIsNotNone(club.deleted_at)

    @patch("django.core.files.storage.default_storage.save")
    def test_club_applies_with_multiple_generations(self, mock_storage):
        """여러 기수의 가입 신청 테스트"""
        mock_storage.return_value = "test-image-path.jpg"

        club, member = ClubService.create_club(
            user=self.owner_user,
            name="신청테스트클럽",
            image=None,
            description="가입 신청 테스트",
            generation_data={
                "name": "1기",
                "start_date": date.today() - timedelta(days=365),
            },
        )

        # 2기 생성
        generation2 = Generation.objects.create(
            club=club,
            name="2기",
            start_date=date.today(),
            end_date=date.today() + timedelta(days=365),
            activated=True,
        )

        # 각 기수에 가입 신청 생성
        ClubApply.objects.create(
            user=self.admin_user, generation=club.current_generation
        )
        ClubApply.objects.create(user=self.member_user, generation=generation2)
        ClubApply.objects.create(user=self.outsider_user, generation=generation2)

        self.client.force_authenticate(user=self.owner_user)

        # 1기 가입 신청 조회
        url = reverse("clubs-applies", kwargs={"pk": club.current_generation.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

        # 2기 가입 신청 조회
        url = reverse("clubs-applies", kwargs={"pk": generation2.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    @patch("django.core.files.storage.default_storage.save")
    def test_club_creation_with_various_data_types(self, mock_storage):
        """다양한 데이터 타입으로 클럽 생성 테스트"""
        mock_storage.return_value = "test-image-path.jpg"

        self.client.force_authenticate(user=self.owner_user)

        # 1. 최소한의 데이터로 클럽 생성
        url = reverse("clubs-list")
        data = {
            "name": "최소클럽",
            "generation": {
                "name": "1기",
                "start_date": "2024-01-01",
            },
        }

        with patch(
            "api.club.services.club_service.ClubService.create_club"
        ) as mock_create:
            mock_club = Mock()
            mock_club.id = 1
            mock_member = Mock()
            mock_create.return_value = (mock_club, mock_member)

            response = self.client.post(url, data, format="json")
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # 2. 완전한 데이터로 클럽 생성
        data = {
            "name": "완전클럽",
            "description": "완전한 설명이 있는 클럽",
            "image": ImageTestUtils.create_test_image(),
            "generation": {
                "name": "1기",
                "start_date": "2024-01-01",
                "end_date": "2024-12-31",
            },
        }

        with patch(
            "api.club.services.club_service.ClubService.create_club"
        ) as mock_create:
            mock_club = Mock()
            mock_club.id = 2
            mock_member = Mock()
            mock_create.return_value = (mock_club, mock_member)

            response = self.client.post(url, data, format="multipart")
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    @patch("django.core.files.storage.default_storage.save")
    def test_generation_creation_edge_cases(self, mock_storage):
        """기수 생성 엣지 케이스 테스트"""
        mock_storage.return_value = "test-image-path.jpg"

        club, member = ClubService.create_club(
            user=self.owner_user,
            name="기수테스트클럽",
            image=None,
            description="기수 테스트",
            generation_data={"name": "1기", "start_date": date.today()},
        )

        self.client.force_authenticate(user=self.owner_user)

        # 1. 과거 날짜로 기수 생성
        url = reverse("clubs-generations", kwargs={"pk": club.id})
        data = {
            "name": "0기",
            "start_date": "2020-01-01",
            "end_date": "2020-12-31",
        }

        with patch(
            "api.club.services.club_service.ClubService.create_generation"
        ) as mock_create:
            mock_generation = Mock()
            mock_generation.id = 2
            mock_create.return_value = mock_generation

            response = self.client.post(url, data, format="json")
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # 2. 종료 날짜 없이 기수 생성
        data = {
            "name": "2기",
            "start_date": "2025-01-01",
        }

        with patch(
            "api.club.services.club_service.ClubService.create_generation"
        ) as mock_create:
            mock_generation = Mock()
            mock_generation.id = 3
            mock_create.return_value = mock_generation

            response = self.client.post(url, data, format="json")
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_serializer_validation_edge_cases(self):
        """시리얼라이저 유효성 검증 엣지 케이스"""
        self.client.force_authenticate(user=self.owner_user)

        url = reverse("clubs-list")

        # 1. 빈 이름으로 클럽 생성 시도
        data = {
            "name": "",
            "generation": {
                "name": "1기",
                "start_date": "2024-01-01",
            },
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # 2. 매우 긴 이름으로 클럽 생성 시도
        data = {
            "name": "a" * 256,  # 255자 초과
            "generation": {
                "name": "1기",
                "start_date": "2024-01-01",
            },
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # 3. 잘못된 날짜 형식으로 기수 생성 시도
        data = {
            "name": "유효한클럽명",
            "generation": {
                "name": "1기",
                "start_date": "잘못된날짜",
            },
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch("django.core.files.storage.default_storage.save")
    def test_concurrent_access_scenarios(self, mock_storage):
        """동시 접근 시나리오 테스트"""
        mock_storage.return_value = "test-image-path.jpg"

        club, member = ClubService.create_club(
            user=self.owner_user,
            name="동시접근테스트클럽",
            image=None,
            description="동시 접근 테스트",
            generation_data={"name": "1기", "start_date": date.today()},
        )

        # 여러 사용자가 동시에 같은 클럽 조회
        clients = []
        for user in [self.owner_user, self.admin_user, self.member_user]:
            client = APIClient()
            client.force_authenticate(user=user)
            clients.append(client)

        url = reverse("clubs-detail", kwargs={"pk": club.id})

        # 동시 요청 시뮬레이션
        responses = []
        for client in clients:
            try:
                response = client.get(url)
                responses.append(response.status_code)
            except Exception:
                responses.append(500)

        # 소유자는 성공, 나머지는 권한에 따라 결과가 달라짐
        self.assertIn(200, responses)  # 적어도 하나는 성공해야 함

    @patch("django.core.files.storage.default_storage.save")
    def test_performance_with_large_data(self, mock_storage):
        """대용량 데이터 처리 성능 테스트"""
        mock_storage.return_value = "test-image-path.jpg"

        club, member = ClubService.create_club(
            user=self.owner_user,
            name="대용량테스트클럽",
            image=None,
            description="대용량 데이터 테스트",
            generation_data={"name": "1기", "start_date": date.today()},
        )

        # 많은 기수 생성 (시뮬레이션)
        for i in range(2, 11):  # 2기부터 10기까지
            Generation.objects.create(
                club=club,
                name=f"{i}기",
                start_date=date.today() + timedelta(days=i * 365),
                activated=False,
            )

        self.client.force_authenticate(user=self.owner_user)

        # 기수 목록 조회 성능 테스트
        url = reverse("clubs-generations", kwargs={"pk": club.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 10)  # 1기부터 10기까지

    def test_http_method_restrictions(self):
        """HTTP 메서드 제한 테스트"""
        self.client.force_authenticate(user=self.owner_user)

        # 존재하지 않는 클럽 ID로 테스트
        test_cases = [
            ("clubs-applies", ["POST", "PUT", "PATCH", "DELETE"]),
            ("clubs-roles", ["POST", "PUT", "PATCH", "DELETE"]),
        ]

        for url_name, forbidden_methods in test_cases:
            url = reverse(url_name, kwargs={"pk": 1})

            for method in forbidden_methods:
                if hasattr(self.client, method.lower()):
                    response = getattr(self.client, method.lower())(url, {})
                    self.assertIn(
                        response.status_code,
                        [
                            status.HTTP_404_NOT_FOUND,
                            status.HTTP_405_METHOD_NOT_ALLOWED,
                        ],
                    )

    @patch("django.core.files.storage.default_storage.save")
    def test_data_consistency_checks(self, mock_storage):
        """데이터 일관성 검증 테스트"""
        mock_storage.return_value = "test-image-path.jpg"

        club, member = ClubService.create_club(
            user=self.owner_user,
            name="일관성테스트클럽",
            image=None,
            description="데이터 일관성 테스트",
            generation_data={"name": "1기", "start_date": date.today()},
        )

        self.client.force_authenticate(user=self.owner_user)

        # 1. 클럽 수정 후 데이터 일관성 확인
        url = reverse("clubs-detail", kwargs={"pk": club.id})
        data = {
            "name": "수정된클럽명",
            "description": "수정된 설명",
        }

        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 수정된 데이터 확인
        club.refresh_from_db()
        self.assertEqual(club.name, "수정된클럽명")
        self.assertEqual(club.description, "수정된 설명")

        # 2. 목록에서도 수정된 이름으로 표시되는지 확인
        url = reverse("clubs-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["club_name"], "수정된클럽명")

    def test_malformed_request_handling(self):
        """잘못된 형식의 요청 처리 테스트"""
        self.client.force_authenticate(user=self.owner_user)

        url = reverse("clubs-list")

        # 1. JSON 형식이 잘못된 요청
        response = self.client.post(
            url, data="잘못된JSON형식", content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # 2. 필수 필드가 누락된 요청
        data = {
            "description": "설명만 있고 이름이 없음"
            # name 필드 누락
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # 3. 중첩된 객체에서 필수 필드 누락
        data = {
            "name": "유효한클럽명",
            "generation": {
                "name": "1기"
                # start_date 필드 누락
            },
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
