from datetime import date, timedelta

import pytest
from rest_framework.test import APIClient

from api.club.models import ClubApply, Generation, GenMember, Member, Role
from api.club.services.club_service import ClubService
from api.club.tests.club_test_utils import ClubTestUtils
from common.test_utils.image_utils import ImageTestUtils


@pytest.fixture
def test_users():
    """테스트용 사용자들 생성"""
    return ClubTestUtils.get_test_users(count=5)


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
def authenticated_client_2(test_users):
    """두 번째 사용자로 인증된 API 클라이언트"""
    client = APIClient()
    user2 = test_users[1]
    client.force_authenticate(user=user2)
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


@pytest.fixture
def generation_with_apply(test_users, mock_storage):
    """가입 신청이 있는 기수 fixture"""
    user1, user2, user3 = test_users[0], test_users[1], test_users[2]

    club, _ = ClubService.create_club(
        user=user1,
        name="신청테스트클럽",
        image=None,
        description="가입 신청 테스트용",
        generation_data={"name": "1기", "start_date": date.today()},
    )

    # 가입 신청 생성
    apply1 = ClubApply.objects.create(user=user2, generation=club.current_generation)
    apply2 = ClubApply.objects.create(user=user3, generation=club.current_generation)

    return club.current_generation, [apply1, apply2]


@pytest.fixture
def club_with_members(test_users, mock_storage):
    """멤버들이 있는 클럽 fixture"""
    user1, user2, user3 = test_users[0], test_users[1], test_users[2]

    club, member1 = ClubService.create_club(
        user=user1,
        name="멤버테스트클럽",
        image=None,
        description="멤버 테스트용",
        generation_data={"name": "1기", "start_date": date.today()},
    )

    # 추가 멤버들 생성
    member2 = Member.objects.create(user=user2, club=club)
    member3 = Member.objects.create(user=user3, club=club)

    # 기수 멤버 매핑 생성
    gen_member2 = GenMember.objects.create(
        member=member2,
        generation=club.current_generation,
        role=Role.objects.get(club=club, name="회원"),
    )
    gen_member3 = GenMember.objects.create(
        member=member3,
        generation=club.current_generation,
        role=Role.objects.get(club=club, name="회원"),
    )

    return (
        club,
        [member1, member2, member3],
        [
            GenMember.objects.get(member=member1, generation=club.current_generation),
            gen_member2,
            gen_member3,
        ],
    )


@pytest.fixture
def multiple_generations(test_users, mock_storage):
    """여러 기수가 있는 클럽 fixture"""
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

    # 2기 생성
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

    return club, [club.generations.get(name="1기"), generation2]


@pytest.fixture
def mock_fcm(mocker):
    """FCM 컴포넌트 모킹"""
    return mocker.patch("common.component.fcm_component.FCMComponent.send_to_users")


@pytest.fixture
def mock_excel(mocker):
    """엑셀 생성 모킹"""
    return mocker.patch(
        "common.utils.excel.create_attendance_excel",
        return_value="/test/path/attendance.xlsx",
    )


@pytest.fixture
def mock_google_sheet(mocker):
    """구글 시트 생성 모킹"""
    return mocker.patch(
        "common.utils.google_sheet.create_attendance_sheet",
        return_value="https://docs.google.com/spreadsheets/test",
    )
