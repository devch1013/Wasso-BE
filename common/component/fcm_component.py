from typing import Dict, List

from firebase_admin import messaging
from loguru import logger

from api.userapp.models import User


class FCMComponent:
    def __init__(self):
        pass

    def send_notification(
        self, token: str, title: str, body: str, data: Dict = None
    ) -> bool:
        """
        FCM 알림을 전송하는 메서드

        Args:
            token: FCM 토큰 (단일 문자열 또는 토큰 리스트)
            title: 알림 제목
            body: 알림 내용
            data: 추가 데이터 (선택사항)

        Returns:
            bool: 전송 성공 여부
        """
        try:
            # 토큰 유효성 검사
            if not token:
                logger.warning("FCM 토큰이 없습니다.")
                return False

            # 토큰 형식 검증
            if not isinstance(token, str) or len(token) < 32:
                logger.warning(f"유효하지 않은 토큰 형식입니다: {token}")
                return False

            # APNS 설정을 포함한 메시지 생성
            message = messaging.Message(
                notification=messaging.Notification(
                    title=title,
                    body=body,
                ),
                apns=messaging.APNSConfig(
                    headers={"apns-priority": "10"},
                    payload=messaging.APNSPayload(
                        aps=messaging.Aps(
                            sound="default",
                            badge=1,
                            content_available=True,
                            mutable_content=True,
                        )
                    ),
                ),
                data=data if data else {},
                token=token if isinstance(token, str) else None,
            )

            # 메시지 전송
            response = messaging.send(message)
            logger.info(f"FCM 알림 전송 성공: {response}")
            return True

        except messaging.UnregisteredError:
            logger.error(f"등록되지 않은 토큰입니다: {token}")
            return False
        except Exception as e:
            logger.error(f"FCM 알림 전송 실패 - 토큰: {token}, 에러: {str(e)}")
            return False

    def send_multicast_notification(
        self, tokens: List[str], title: str, body: str, data: Dict = None
    ) -> Dict:
        """
        여러 디바이스에 FCM 알림을 전송하는 메서드

        Args:
            tokens: FCM 토큰 리스트
            title: 알림 제목
            body: 알림 내용
            data: 추가 데이터 (선택사항)

        Returns:
            Dict: 성공 및 실패 결과
        """
        try:
            # 토큰 유효성 검사
            if not tokens:
                print("FCM 토큰 리스트가 비어있습니다.")
                return {"success_count": 0, "failure_count": 0}

            # APNS 설정을 포함한 멀티캐스트 메시지 생성
            message = messaging.MulticastMessage(
                notification=messaging.Notification(
                    title=title,
                    body=body,
                ),
                apns=messaging.APNSConfig(
                    headers={"apns-priority": "10"},
                    payload=messaging.APNSPayload(
                        aps=messaging.Aps(
                            sound="default",
                            badge=1,
                            content_available=True,
                            mutable_content=True,
                        )
                    ),
                ),
                data=data if data else {},
                tokens=tokens,
            )

            # 메시지 전송
            response = messaging.send_each_for_multicast(message)
            logger.info(response)

            return {
                "success_count": response.success_count,
                "failure_count": response.failure_count,
            }

        except Exception as e:
            print(f"FCM 멀티캐스트 알림 전송 실패: {str(e)}")
            return {"success_count": 0, "failure_count": len(tokens)}

    def send_to_users(
        self, users: List[User], title: str, body: str, data: Dict = None
    ):
        tokens = [
            user.fcm_token for user in users if user.fcm_token and user.push_allow
        ]
        return self.send_multicast_notification(tokens, title, body, data)

    def send_to_user(self, user: User, title: str, body: str, data: Dict = None):
        if not user.push_allow:
            return
        return self.send_notification(user.fcm_token, title, body, data)
