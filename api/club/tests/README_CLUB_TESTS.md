# Club Views 테스트 가이드

## 개요

이 문서는 `ClubViewSet`에 대한 포괄적인 테스트 모음에 대한 설명입니다. 모든 API 엔드포인트, 권한, 엣지 케이스를 커버하는 철저한 테스트를 제공합니다.

## 테스트 파일 구조

### 1. `test_club_views_comprehensive.py`
ClubViewSet의 모든 주요 기능에 대한 기본 테스트

**포함된 테스트:**
- ✅ `list()` - 클럽 목록 조회
- ✅ `retrieve()` - 클럽 상세 조회
- ✅ `create()` - 클럽 생성
- ✅ `update()` - 클럽 정보 수정
- ✅ `destroy()` - 클럽 삭제
- ✅ `applies()` 액션 - 가입 신청 목록
- ✅ `roles()` 액션 - 역할 목록
- ✅ `generations()` 액션 - 기수 관리 (GET/POST)

**테스트 시나리오:**
- 성공 케이스
- 실패 케이스 (404, 400, 401)
- 권한 검증
- 데이터 유효성 검증
- 소프트 삭제 동작

### 2. `test_club_views_edge_cases.py`
엣지 케이스와 복잡한 시나리오에 대한 상세 테스트

**포함된 테스트:**
- ✅ 멤버별 권한 테스트 (소유자/관리자/일반회원/외부인)
- ✅ 여러 기수 처리
- ✅ 소프트 삭제 동작
- ✅ 동시 접근 시나리오
- ✅ 대용량 데이터 처리
- ✅ HTTP 메서드 제한
- ✅ 데이터 일관성 검증
- ✅ 잘못된 요청 처리

## 테스트 커버리지

### API 엔드포인트 커버리지
| 엔드포인트 | HTTP 메서드 | 테스트 상태 | 설명 |
|-----------|-------------|------------|------|
| `/clubs/` | GET | ✅ | 클럽 목록 조회 |
| `/clubs/` | POST | ✅ | 클럽 생성 |
| `/clubs/{id}/` | GET | ✅ | 클럽 상세 조회 |
| `/clubs/{id}/` | PUT/PATCH | ✅ | 클럽 정보 수정 |
| `/clubs/{id}/` | DELETE | ✅ | 클럽 삭제 |
| `/clubs/{id}/applies/` | GET | ✅ | 가입 신청 목록 |
| `/clubs/{id}/roles/` | GET | ✅ | 역할 목록 |
| `/clubs/{id}/generations/` | GET | ✅ | 기수 목록 |
| `/clubs/{id}/generations/` | POST | ✅ | 기수 생성 |

### 권한 테스트 커버리지
| 사용자 타입 | 테스트 상태 | 설명 |
|------------|------------|------|
| 인증되지 않은 사용자 | ✅ | 모든 접근 차단 |
| 클럽 소유자 | ✅ | 모든 권한 허용 |
| 클럽 관리자 | ✅ | 제한된 권한 |
| 일반 회원 | ✅ | 조회만 가능 |
| 외부인 | ✅ | 접근 차단 |

### 데이터 유효성 테스트
- ✅ 필수 필드 누락
- ✅ 잘못된 데이터 타입
- ✅ 길이 제한 초과
- ✅ 중복 클럽명
- ✅ 잘못된 날짜 형식
- ✅ 잘못된 JSON 형식

## 실행 방법

### 전체 클럽 테스트 실행
```bash
python manage.py test api.club.tests.test_club_views_comprehensive
python manage.py test api.club.tests.test_club_views_edge_cases
```

### 특정 테스트 클래스 실행
```bash
python manage.py test api.club.tests.test_club_views_comprehensive.ClubViewSetComprehensiveTestCase
```

### 특정 테스트 메서드 실행
```bash
python manage.py test api.club.tests.test_club_views_comprehensive.ClubViewSetComprehensiveTestCase.test_list_clubs_success
```

### 커버리지와 함께 실행
```bash
coverage run --source='.' manage.py test api.club.tests.test_club_views_comprehensive
coverage report
coverage html
```

## 테스트 환경 설정

### 필요한 의존성
- Django Test Framework
- Django REST Framework TestCase
- PIL (이미지 처리)
- Mock (unittest.mock)

### Mock 설정
모든 S3 저장소 작업은 mock 처리되어 실제 파일 업로드 없이 테스트가 진행됩니다.

```python
@patch("django.core.files.storage.default_storage.save")
def test_method(self, mock_storage):
    mock_storage.return_value = "test-image-path.jpg"
    # 테스트 코드
```

## 테스트 데이터

### 테스트 사용자
- `owner_user`: 클럽 소유자 권한
- `admin_user`: 클럽 관리자 권한  
- `member_user`: 일반 회원 권한
- `outsider_user`: 클럽 비회원

### 테스트 클럽
각 테스트마다 독립적인 클럽과 기수가 생성됩니다.

### 테스트 이미지
`ImageTestUtils.create_test_image()`를 사용하여 테스트용 이미지를 생성합니다.

## 주요 테스트 시나리오

### 1. 기본 CRUD 작업
- 클럽 생성, 조회, 수정, 삭제
- 유효성 검증
- 권한 확인

### 2. 복잡한 관계 처리
- 여러 기수 관리
- 멤버-클럽-역할 관계
- 가입 신청 처리

### 3. 엣지 케이스
- 삭제된 데이터 처리
- 동시 접근
- 대용량 데이터
- 잘못된 요청

### 4. 보안 테스트
- 인증/인가 검증
- 권한별 접근 제어
- 데이터 누출 방지

## 기대 동작

### 성공 케이스
- 적절한 HTTP 상태 코드 반환
- 올바른 데이터 구조
- 권한에 맞는 접근 허용

### 실패 케이스
- 적절한 에러 상태 코드
- 명확한 에러 메시지
- 데이터 무결성 유지

## 유지보수 가이드

### 새로운 기능 추가 시
1. 해당 기능에 대한 테스트 메서드 추가
2. 성공/실패 케이스 모두 작성
3. 권한 테스트 포함
4. 엣지 케이스 고려

### 기존 기능 수정 시
1. 관련 테스트 업데이트
2. 영향받는 다른 테스트 확인
3. 회귀 테스트 실행

## 문제 해결

### 자주 발생하는 문제
1. **S3 Mock 설정**: `@patch("django.core.files.storage.default_storage.save")` 데코레이터 확인
2. **URL 패턴**: `reverse()` 함수에 올바른 URL 이름 사용
3. **권한 설정**: `self.client.force_authenticate(user=user)` 호출 확인

### 디버깅 팁
- `print(response.data)`: 응답 데이터 확인
- `print(response.status_code)`: 상태 코드 확인
- `self.maxDiff = None`: 전체 diff 출력

## 성능 고려사항

- 각 테스트는 독립적으로 실행
- 테스트 데이터는 자동으로 정리
- Mock을 사용하여 외부 의존성 제거
- 트랜잭션 롤백으로 빠른 실행

## 결론

이 테스트 모음은 ClubViewSet의 모든 기능을 철저히 검증하며, 안정적이고 신뢰할 수 있는 API를 보장합니다. 새로운 기능 추가나 기존 기능 수정 시 이 테스트들을 실행하여 회귀 문제를 방지할 수 있습니다.
