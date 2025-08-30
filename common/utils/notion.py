import os
import threading
from typing import Dict, List

import requests

from api.club.models import Generation, GenMember
from api.event.models import Attendance, AttendanceStatus, Event
from api.userapp.models import User
from common.component import FCMComponent

fcm_component = FCMComponent()


class NotionAttendanceManager:
    def __init__(self):
        self.headers = {
            "Authorization": f"Bearer {os.getenv('NOTION_TOKEN')}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28",
        }
        self.base_url = "https://api.notion.com/v1"

    def _create_database(
        self, notion_parent_page_id: str, title: str, properties: Dict
    ) -> str:
        """Create a new Notion database"""
        url = f"{self.base_url}/databases"
        payload = {
            "parent": {"page_id": notion_parent_page_id},
            "title": [{"type": "text", "text": {"content": title}}],
            "properties": properties,
        }
        response = requests.post(url, headers=self.headers, json=payload)
        response.raise_for_status()
        return response.json()["id"]

    def _update_database_row(self, database_id: str, row: Dict):
        """Update a single database row"""
        url = f"{self.base_url}/pages"
        payload = {"parent": {"database_id": database_id}, "properties": row}
        response = requests.post(url, headers=self.headers, json=payload)
        response.raise_for_status()
        return response.json()

    def _update_database_rows(self, database_id: str, rows: List[Dict]):
        """Update database rows with attendance data - sequential processing"""
        results = []
        for i, row in enumerate(rows):
            # 진행 상황 출력 (선택 사항)
            print(f"Updating row {i+1}/{len(rows)}")
            result = self._update_database_row(database_id, row)
            results.append(result)
            # 각 요청 사이에 약간의 지연 추가 (Notion API 속도 제한 방지)
            # if i < len(rows) - 1:
            #     time.sleep(0.5)
        return results

    def _get_database_pages(self, database_id: str) -> List[str]:
        """Get all pages in a database to delete them"""
        url = f"{self.base_url}/databases/{database_id}/query"
        response = requests.post(url, headers=self.headers)
        response.raise_for_status()
        return [page["id"] for page in response.json().get("results", [])]

    def _delete_database_pages(self, database_id: str):
        """Archive all existing pages in the database"""
        page_ids = self._get_database_pages(database_id)
        for page_id in page_ids:
            url = f"{self.base_url}/pages/{page_id}"
            payload = {"archived": True}
            response = requests.patch(url, headers=self.headers, json=payload)
            response.raise_for_status()

    def _update_database_schema(
        self, database_id: str, properties: Dict, title: str = None
    ):
        """Update database schema with new properties and optionally the title"""
        url = f"{self.base_url}/databases/{database_id}"
        payload = {"properties": properties}

        # Add title to payload if provided
        if title:
            payload["title"] = [{"type": "text", "text": {"content": title}}]

        response = requests.patch(url, headers=self.headers, json=payload)
        response.raise_for_status()

    def update_attendance_database_async(
        self, generation: Generation, database_id: str = None, user: User = None
    ):
        """
        비동기적으로 출석 정보를 업데이트하고 완료 시 사용자에게 알림
        """

        def background_task():
            try:
                self.update_attendance_database(generation, database_id)
                # 작업 완료 후 알림 전송
                if user:
                    fcm_component.send_to_user(
                        user,
                        "노션 동기화 완료",
                        f"{generation.club.name} - {generation.name}의 출석 정보가 노션에 성공적으로 업데이트되었습니다.",
                    )
            except Exception as e:
                # 오류 발생 시 알림
                if user:
                    fcm_component.send_to_user(
                        user,
                        "노션 동기화 실패",
                        f"{generation.club.name} - {generation.name}의 출석 정보 업데이트 중 오류가 발생했습니다: {str(e)}",
                    )
                raise e

        # 별도 스레드에서 작업 실행
        thread = threading.Thread(target=background_task)
        thread.daemon = True
        thread.start()

        return {
            "status": "processing",
            "message": "노션 데이터베이스 업데이트가 백그라운드에서 처리 중입니다. 완료 시 알림이 발송됩니다.",
        }

    def update_attendance_database(
        self, generation: Generation, database_id: str = None
    ):
        """
        Main function to create/update attendance database for a generation
        If database_id is provided, updates existing database instead of creating new one
        """
        # Get required data from Django models
        club = generation.club
        events = Event.objects.filter(generation=generation).order_by(
            "date", "start_datetime"
        )
        gen_members = GenMember.objects.filter(generation=generation, is_current=True)

        # Create database title and properties
        db_title = f"{club.name} - {generation.name} - 출석 정보"
        properties = {
            "이름": {"title": {}},
        }

        # Add event columns
        for event in events:
            column_name = f"{event.date.strftime('%m/%d')} {event.title}"
            properties[column_name] = {
                "select": {
                    "options": [
                        {"name": "출석", "color": "green"},
                        {"name": "지각", "color": "yellow"},
                        {"name": "결석", "color": "red"},
                        {"name": "미인증", "color": "gray"},
                    ]
                }
            }

        if database_id:
            # Check if database exists before updating
            try:
                # Verify database exists by making a request to get it
                url = f"{self.base_url}/databases/{database_id}"
                response = requests.get(url, headers=self.headers)
                response.raise_for_status()

                # Update existing database
                self._update_database_schema(database_id, properties, db_title)
                # Clear existing data
                self._delete_database_pages(database_id)
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 404:
                    # Database not found, raise a more descriptive error
                    raise ValueError(
                        f"Notion database with ID {database_id} not found. Please check the database ID."
                    ) from e
                else:
                    # Re-raise other HTTP errors
                    raise
        else:
            raise ValueError("Database ID is required")
        # else:
        #     # Create new database
        #     database_id = self._create_database(page_id, db_title, properties)

        # Prepare and update rows
        rows = []
        for gen_member in gen_members:
            member = gen_member.member
            row_data = {
                "이름": {"title": [{"text": {"content": member.user.username}}]}
            }

            for event in events:
                column_name = f"{event.date.strftime('%m/%d')} {event.title}"
                attendance = (
                    Attendance.objects.filter(
                        generation_mapping=gen_member, event=event
                    )
                    .order_by("-modified_at")
                    .first()
                )

                status = "미정"
                if attendance:
                    if attendance.status == AttendanceStatus.PRESENT:
                        status = "출석"
                    elif attendance.status == AttendanceStatus.LATE:
                        status = "지각"
                    elif attendance.status == AttendanceStatus.ABSENT:
                        status = "결석"

                row_data[column_name] = {"select": {"name": status}}

            rows.append(row_data)

        # Update database with rows
        self._update_database_rows(database_id, rows)

        return database_id
