from datetime import date, time
from unittest.mock import MagicMock, patch

from django.test import TestCase

from api.club.models import Club, Generation, GenMember, Member
from api.event.models import Event, Attendance, AttendanceStatus
from common.utils.google_sheet import create_attendance_sheet

from api.userapp.models import User

class GoogleSheetTest(TestCase):
    def setUp(self):
        # 테스트 데이터 생성
        self.user1 = User.objects.create(username="test_user1", identifier="test_user1")
        self.user2 = User.objects.create(username="test_user2", identifier="test_user2")
        
        self.club = Club.objects.create(name="테스트 동아리")
        self.generation = Generation.objects.create(
            club=self.club,
            name="1기",
            start_date=date(2024, 1, 1)
        )
        
        # 멤버 생성
        self.member1 = Member.objects.create(user=self.user1, club=self.club)
        self.member2 = Member.objects.create(user=self.user2, club=self.club)
        
        # GenerationMapping 생성
        self.mapping1 = GenMember.objects.create(
            member=self.member1,
            generation=self.generation
        )
        self.mapping2 = GenMember.objects.create(
            member=self.member2,
            generation=self.generation
        )
        
        # 이벤트 생성
        self.event1 = Event.objects.create(
            generation=self.generation,
            title="첫 번째 모임",
            date=date(2024, 1, 15),
            start_time=time(18, 0),
            end_time=time(20, 0),
            start_minutes=0,
            late_minutes=10,
            fail_minutes=30,
            location="테스트 장소"
        )
        self.event2 = Event.objects.create(
            generation=self.generation,
            title="두 번째 모임",
            date=date(2024, 1, 22),
            start_time=time(18, 0),
            end_time=time(20, 0),
            start_minutes=0,
            late_minutes=10,
            fail_minutes=30,
            location="테스트 장소"
        )
        
        # 출석 정보 생성
        Attendance.objects.create(
            generation_mapping=self.mapping1,
            event=self.event1,
            status=AttendanceStatus.PRESENT
        )
        Attendance.objects.create(
            generation_mapping=self.mapping1,
            event=self.event2,
            status=AttendanceStatus.LATE
        )
        Attendance.objects.create(
            generation_mapping=self.mapping2,
            event=self.event1,
            status=AttendanceStatus.ABSENT
        )
        Attendance.objects.create(
            generation_mapping=self.mapping2,
            event=self.event2,
            status=AttendanceStatus.PRESENT
        )

    @patch('common.utils.google_sheet.service_account.Credentials')
    @patch('common.utils.google_sheet.build')
    def test_create_attendance_sheet(self, mock_build, mock_credentials):
        # Google Sheets API 응답 모킹
        mock_service = MagicMock()
        mock_build.return_value = mock_service
        
        mock_spreadsheet = {
            'spreadsheetId': 'test_spreadsheet_id'
        }
        mock_service.spreadsheets().create().execute.return_value = mock_spreadsheet
        
        # 함수 실행
        result = create_attendance_sheet(self.generation)
        
        # 검증
        self.assertEqual(
            result,
            'https://docs.google.com/spreadsheets/d/test_spreadsheet_id'
        )
        
        # API 호출 검증
        mock_service.spreadsheets().create().execute.assert_called_once()
        mock_service.spreadsheets().values().update().execute.assert_called_once()
        mock_service.spreadsheets().batchUpdate().execute.assert_called_once()
        
        # 데이터 형식 검증 - 수정된 부분
        mock_calls = mock_service.mock_calls
        
        # update 호출에서 사용된 인자 찾기
        for call in mock_calls:
            if 'values().update' in str(call):
                # logger.info(f"Update call: {call}")
                # call[2]는 kwargs를 포함
                values = call[2]['body']['values']
                
                # 헤더 검증
                self.assertEqual(values[0][0], '이름(총 2명)')
                self.assertEqual(values[0][1], '01/15 첫 번째 모임')
                self.assertEqual(values[0][2], '01/22 두 번째 모임')
                
                # 데이터 검증
                self.assertEqual(values[1][0], 'test_user1')
                self.assertEqual(values[1][1], '출석')
                self.assertEqual(values[1][2], '지각')
                
                self.assertEqual(values[2][0], 'test_user2')
                self.assertEqual(values[2][1], '결석')
                self.assertEqual(values[2][2], '출석')
                break