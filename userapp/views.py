from .models import User
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
import requests
from rest_framework_simplejwt.tokens import RefreshToken

class KakaoLoginView(APIView):
    def post(self, request):
        kakao_token = request.query_params.get('kakao_token')
        if not kakao_token:
            return Response({'error': 'Kakao token is required'}, status=status.HTTP_400_BAD_REQUEST)

        # 카카오 API로 사용자 정보 가져오기
        user_info = self.get_kakao_user_info(kakao_token)
        if not user_info:
            return Response({'error': 'Invalid Kakao token'}, status=status.HTTP_401_UNAUTHORIZED)

        # 사용자 생성 또는 조회
        user, _ = User.objects.get_or_create(
            identifier=str(user_info['id']),
            defaults={
                'username': user_info.get('properties', {}).get('nickname', ''),
            }
        )

        # JWT 토큰 생성
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'access_token': str(refresh.access_token),
            'refresh_token': str(refresh),
            'token_type': 'bearer',
        })

    def get_kakao_user_info(self, access_token):
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-type": "application/x-www-form-urlencoded;charset=utf-8"
        }
        response = requests.get("https://kapi.kakao.com/v2/user/me", headers=headers)
        if response.status_code == 200:
            return response.json()
        return None
