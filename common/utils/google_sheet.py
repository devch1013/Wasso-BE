from google.oauth2 import service_account
from googleapiclient.discovery import build

from api.club.models import Generation, GenMember
from api.event.models import Attendance, AttendanceStatus, Event


def create_attendance_sheet(generation: Generation) -> str:
    """
    특정 기수의 출석 정보를 구글 시트로 생성합니다.

    Args:
        generation: Generation 모델

    Returns:
        생성된 구글 시트의 URL
    """
    # Google Sheets API 설정
    SCOPES = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive.file",
    ]
    credentials = service_account.Credentials.from_service_account_file(
        "wasso-google-sheet.json", scopes=SCOPES
    )
    service = build("sheets", "v4", credentials=credentials)

    # 데이터 가져오기
    events = Event.objects.filter(generation=generation).order_by("date", "start_time")
    generation_mappings = GenMember.objects.filter(
        generation=generation
    ).select_related("member__user")
    attendances = Attendance.objects.filter(
        event__in=events, generation_mapping__in=generation_mappings
    )

    # 시트 제목 생성
    sheet_title = f"{generation.club.name} - {generation.name} - 출석 정보"

    # 헤더 행 생성 (날짜 + 이벤트명 + 통계)
    headers = [f"이름(총 {len(generation_mappings)}명)"]
    for event in events:
        event_header = f"{event.date.strftime('%m/%d')} {event.title}"
        headers.append(event_header)
    headers.extend(["출석", "지각", "결석"])  # 통계 컬럼 추가

    # 출석 데이터 매트릭스 생성
    attendance_data = []
    for mapping in generation_mappings:
        row = [mapping.member.user.username]  # 첫 열은 멤버 이름
        present_count = late_count = absent_count = 0

        for event in events:
            attendance = attendances.filter(
                event=event, generation_mapping=mapping
            ).first()
            status = (
                "출석"
                if attendance and attendance.status == AttendanceStatus.PRESENT
                else "지각"
                if attendance and attendance.status == AttendanceStatus.LATE
                else "결석"
                if attendance and attendance.status == AttendanceStatus.ABSENT
                else "-"
            )
            row.append(status)

            # 상태별 카운트
            if status == "출석":
                present_count += 1
            elif status == "지각":
                late_count += 1
            elif status == "결석":
                absent_count += 1

        # 통계 추가
        row.extend([present_count, late_count, absent_count])
        attendance_data.append(row)

    # 이벤트별 통계 행 추가 (출석/지각/결석 별도 행)
    present_stats = ["출석"]
    late_stats = ["지각"]
    absent_stats = ["결석"]

    for i in range(len(events)):
        column_data = [
            row[i + 1] for row in attendance_data
        ]  # i+1은 이름 컬럼을 건너뛰기 위함
        present_count = column_data.count("출석")
        late_count = column_data.count("지각")
        absent_count = column_data.count("결석")

        present_stats.append(str(present_count))
        late_stats.append(str(late_count))
        absent_stats.append(str(absent_count))

    # 마지막 통계 컬럼들은 빈칸으로 채움
    present_stats.extend([""] * 3)
    late_stats.extend([""] * 3)
    absent_stats.extend([""] * 3)

    # 새 스프레드시트 생성
    spreadsheet = {"properties": {"title": sheet_title}}
    spreadsheet = service.spreadsheets().create(body=spreadsheet).execute()
    spreadsheet_id = spreadsheet["spreadsheetId"]

    # 데이터 업데이트
    values = [headers] + attendance_data + [present_stats, late_stats, absent_stats]
    body = {"values": values}
    service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id, range="A1", valueInputOption="RAW", body=body
    ).execute()

    # 스타일링 적용
    requests = [
        {
            "repeatCell": {
                "range": {"sheetId": 0, "startRowIndex": 0, "endRowIndex": 1},
                "cell": {
                    "userEnteredFormat": {
                        "backgroundColor": {"red": 0.9, "green": 0.9, "blue": 0.9},
                        "textFormat": {"bold": True},
                    }
                },
                "fields": "userEnteredFormat(backgroundColor,textFormat)",
            }
        },
        {
            "repeatCell": {
                "range": {
                    "sheetId": 0,
                    "startColumnIndex": len(headers) - 3,
                    "endColumnIndex": len(headers),
                },
                "cell": {
                    "userEnteredFormat": {
                        "backgroundColor": {"red": 0.95, "green": 0.95, "blue": 0.95},
                    }
                },
                "fields": "userEnteredFormat(backgroundColor)",
            }
        },
        {
            "repeatCell": {
                "range": {
                    "sheetId": 0,
                    "startRowIndex": len(attendance_data) + 1,
                    "endRowIndex": len(attendance_data) + 4,  # 3개 행으로 변경
                },
                "cell": {
                    "userEnteredFormat": {
                        "backgroundColor": {"red": 0.95, "green": 0.95, "blue": 0.95},
                        "textFormat": {"bold": True},
                    }
                },
                "fields": "userEnteredFormat(backgroundColor,textFormat)",
            }
        },
        {
            "addConditionalFormatRule": {
                "rule": {
                    "ranges": [{"sheetId": 0, "startRowIndex": 1}],
                    "booleanRule": {
                        "condition": {
                            "type": "TEXT_EQ",
                            "values": [{"userEnteredValue": "출석"}],
                        },
                        "format": {
                            "backgroundColor": {
                                "red": 0.85,
                                "green": 0.92,
                                "blue": 0.85,
                            }
                        },
                    },
                }
            }
        },
        {
            "addConditionalFormatRule": {
                "rule": {
                    "ranges": [{"sheetId": 0, "startRowIndex": 1}],
                    "booleanRule": {
                        "condition": {
                            "type": "TEXT_EQ",
                            "values": [{"userEnteredValue": "지각"}],
                        },
                        "format": {
                            "backgroundColor": {"red": 1.0, "green": 0.95, "blue": 0.8}
                        },
                    },
                }
            }
        },
        {
            "addConditionalFormatRule": {
                "rule": {
                    "ranges": [{"sheetId": 0, "startRowIndex": 1}],
                    "booleanRule": {
                        "condition": {
                            "type": "TEXT_EQ",
                            "values": [{"userEnteredValue": "결석"}],
                        },
                        "format": {
                            "backgroundColor": {"red": 1.0, "green": 0.85, "blue": 0.85}
                        },
                    },
                }
            }
        },
    ]

    service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id, body={"requests": requests}
    ).execute()

    # Drive API를 사용하여 권한 설정
    drive_service = build("drive", "v3", credentials=credentials)
    drive_service.permissions().create(
        fileId=spreadsheet_id, body={"role": "reader", "type": "anyone"}
    ).execute()

    return f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}"
