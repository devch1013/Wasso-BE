from datetime import timedelta
from functools import wraps
from unittest.mock import patch

from django.utils import timezone

from api.club.services.apply_service import ApplyService
from api.club.services.club_service import ClubService
from api.event.models import Attendance, AttendanceStatus, Event
from api.userapp.models import User
from common.test_utils.image_utils import ImageTestUtils


def mock_storage(func):
    """Storage mocking을 위한 데코레이터"""

    @wraps(func)
    def wrapper(*args, **kwargs):
        with patch("django.core.files.storage.default_storage.save") as mock_save:
            mock_save.return_value = "test-image-path.jpg"
            return func(*args, **kwargs)

    return wrapper


class EntityCreator:
    def __init__(self):
        self.club = None
        self.generation = None
        self.users = []
        self.members = []
        self.events = []
        self.attendances = []

    @mock_storage
    def create_club(self, club_name=None, user_name=None):
        """클럽과 기본 Role을 생성"""
        self.users.append(
            User.objects.create_user(username=user_name, identifier=user_name)
        )

        name = club_name or "Test Club"
        self.club, member = ClubService.create_club(
            user=self.users[0],
            name=name,
            image=ImageTestUtils.create_test_image(),
            description=f"{name} Description",
            generation_data={
                "name": "Test Generation",
                "start_date": timezone.now().date(),
                "end_date": (timezone.now() + timedelta(days=180)).date(),
            },
        )
        self.members.append(member)
        self.generation = self.club.current_generation
        return self.club

    @mock_storage
    def _create_users(self, count=1, start_index=0):
        """여러 User 생성"""
        for i in range(start_index, start_index + count):
            user = User.objects.create_user(
                username=f"testuser{i}",
                identifier=f"testuser{i}",
                profile_image=ImageTestUtils.create_test_image(),
            )
            self.users.append(user)
        return self.users

    def create_members(self, user_count=1):
        """User, Member, GenerationMapping 생성"""

        users = self.create_users(count=user_count)

        for user in users:
            member, generation_mapping = ApplyService.join_generation(
                user, self.generation
            )
            self.members.append(member)

        return self.members

    @mock_storage
    def create_event(self, count=1):
        """Event 생성"""
        if not self.generation:
            self.create_generation()

        for i in range(count):
            event = Event.objects.create(
                generation=self.generation,
                title=f"Test Event {i}",
                description=f"Test Description {i}",
                date=timezone.now().date(),
                start_time="10:00",
                end_time="11:00",
                start_minutes=0,
                late_minutes=10,
                fail_minutes=20,
                location="Test Location",
                location_link="Test Location Link",
                attendance_type="QR",
                images=[ImageTestUtils.create_test_image()],
            )
            self.events.append(event)
        return self.events

    def create_attendances(self, status_list=None):
        """Attendance 생성"""
        if not self.events or not self.generation_mappings:
            raise ValueError("Events and members must be created first")

        status_list = status_list or [AttendanceStatus.PRESENT] * len(
            self.generation_mappings
        )

        for event in self.events:
            for mapping, status in zip(self.generation_mappings, status_list):
                attendance = Attendance.objects.create(
                    event=event, generation_mapping=mapping, status=status
                )
                self.attendances.append(attendance)
        return self.attendances
