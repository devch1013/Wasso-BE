from typing import Dict, List, Union

from firebase_admin import messaging


class FCMComponent:
    def __init__(self):
        pass

    def send_notification(
        self, token: Union[str, List[str]], title: str, body: str, data: Dict = None
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
            print(token)
            # 메시지 생성
            message = messaging.Message(
                notification=messaging.Notification(
                    title=title,
                    body=body,
                ),
                data=data if data else {},
                token=token if isinstance(token, str) else None,
            )

            # 메시지 전송
            response = messaging.send(message)
            print("response", response)
            return True if response else False

        except Exception as e:
            print(f"FCM 알림 전송 실패: {str(e)}")
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
            # 메시지 생성
            message = messaging.MulticastMessage(
                notification=messaging.Notification(
                    title=title,
                    body=body,
                ),
                data=data if data else {},
                tokens=tokens,
            )

            # 메시지 전송
            response = messaging.send_multicast(message)

            return {
                "success_count": response.success_count,
                "failure_count": response.failure_count,
            }

        except Exception as e:
            print(f"FCM 멀티캐스트 알림 전송 실패: {str(e)}")
            return {"success_count": 0, "failure_count": len(tokens)}
