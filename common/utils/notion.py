from typing import Dict, List
import requests

from api.club.models import Generation, Member
from api.event.models import Event, Attendance, AttendanceStatus
import os
class NotionAttendanceManager:
    def __init__(self, notion_parent_page_id: str):
        self.headers = {
            "Authorization": f"Bearer {os.getenv('NOTION_TOKEN')}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        }
        self.parent_page_id = notion_parent_page_id
        self.base_url = "https://api.notion.com/v1"

    def _create_database(self, title: str, properties: Dict) -> str:
        """Create a new Notion database"""
        url = f"{self.base_url}/databases"
        payload = {
            "parent": {"page_id": self.parent_page_id},
            "title": [{"type": "text", "text": {"content": title}}],
            "properties": properties
        }
        response = requests.post(url, headers=self.headers, json=payload)
        response.raise_for_status()
        return response.json()["id"]

    def _update_database_rows(self, database_id: str, rows: List[Dict]):
        """Update database rows with attendance data"""
        for row in rows:
            url = f"{self.base_url}/pages"
            payload = {
                "parent": {"database_id": database_id},
                "properties": row
            }
            response = requests.post(url, headers=self.headers, json=payload)
            response.raise_for_status()

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
            payload = {
                "archived": True
            }
            response = requests.patch(url, headers=self.headers, json=payload)
            response.raise_for_status()

    def _update_database_schema(self, database_id: str, properties: Dict):
        """Update database schema with new properties"""
        url = f"{self.base_url}/databases/{database_id}"
        payload = {
            "properties": properties
        }
        response = requests.patch(url, headers=self.headers, json=payload)
        response.raise_for_status()

    def update_attendance_database(self, generation_id: int, database_id: str = None):
        """
        Main function to create/update attendance database for a generation
        If database_id is provided, updates existing database instead of creating new one
        """
        # Get required data from Django models
        generation = Generation.objects.get(id=generation_id)
        club = generation.club
        events = Event.objects.filter(generation=generation).order_by('date', 'start_time')
        members = Member.objects.filter(
            generationmapping__generation=generation,
            generationmapping__is_current=True
        )

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
                        {"name": "미정", "color": "gray"}
                    ]
                }
            }

        if database_id:
            # Update existing database
            self._update_database_schema(database_id, properties)
            # Clear existing data
            self._delete_database_pages(database_id)
        else:
            # Create new database
            database_id = self._create_database(db_title, properties)

        # Prepare and update rows
        rows = []
        for member in members:
            row_data = {
                "이름": {"title": [{"text": {"content": member.user.username}}]}
            }

            for event in events:
                column_name = f"{event.date.strftime('%m/%d')} {event.title}"
                attendance = Attendance.objects.filter(
                    generation_mapping__member=member,
                    event=event
                ).first()

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
