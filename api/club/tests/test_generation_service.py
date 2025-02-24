from django.test import TestCase
from api.event.models import Event, Attendance, AttendanceStatus
from api.userapp.models import User
from api.club.services.club_service import ClubService
from api.club.services.apply_service import ApplyService
from common.test_utils.image_utils import ImageTestUtils
from api.club.services.generation_service import GenerationService
from unittest.mock import patch

class GenerationViewTest(TestCase):
    @patch("django.core.files.storage.default_storage.save")
    def setUp(self, mock_storage):
        mock_storage.return_value = "test-image-path.jpg"
        
        self.user = User.objects.create_user(username="btestuser", identifier="testuser")
        self.user1 = User.objects.create_user(username="atestuser", identifier="testuser1")
        self.user2 = User.objects.create_user(username="dtestuser", identifier="testuser2")
        self.user3 = User.objects.create_user(username="ctestuser", identifier="testuser3")
        
        self.club, self.member = ClubService.create_club(
            name="Test Club",
            description="Test Description",
            image=ImageTestUtils.create_test_image(),
            user=self.user,
            generation_data={
                "name": "Test Generation",
                "start_date": "2021-01-01",
                "end_date": "2021-01-01"
            }
        )
        self.generation = self.club.current_generation
        
        self.event = Event.objects.create(
            generation=self.generation,
            title="Test Event",
            description="Test Description",
            date="2021-01-01",
            start_time="10:00",
            end_time="11:00",
            start_minutes=0,
            late_minutes=10,
            fail_minutes=20,
            location="Test Location",
            location_link="Test Location Link",
            attendance_type="QR"
        )
        
        self.member1, self.generation_mapping1 = ApplyService.join_generation(self.user1, self.generation)
        self.member2, self.generation_mapping2 = ApplyService.join_generation(self.user2, self.generation)
        self.member3, self.generation_mapping3 = ApplyService.join_generation(self.user3, self.generation)
        
        
    def test_get_generation_stats(self):
        """기수 출석 통계 테스트"""
        Attendance.objects.create(
            event=self.event,
            generation_mapping=self.generation_mapping1,
            status=AttendanceStatus.PRESENT
        )
        
        Attendance.objects.create(
            event=self.event,
            generation_mapping=self.generation_mapping2,
            status=AttendanceStatus.LATE
        )
        
        Attendance.objects.create(
            event=self.event,
            generation_mapping=self.generation_mapping3,
            status=AttendanceStatus.ABSENT
        )
        stats = GenerationService.get_generation_stats(self.generation.id)
        # for stat in stats:
        #     logger.info("{}: {}", stat.member.user.username, stat.present_count)
        #     logger.info("{}: {}", stat.member.user.username, stat.late_count)
        #     logger.info("{}: {}", stat.member.user.username, stat.absent_count)
        self.assertEqual(stats.count(), 4)
        self.assertEqual(stats.filter(attendance__status=AttendanceStatus.PRESENT).count(), 1)
        self.assertEqual(stats.filter(attendance__status=AttendanceStatus.LATE).count(), 1)
        self.assertEqual(stats.filter(attendance__status=AttendanceStatus.ABSENT).count(), 1)
        