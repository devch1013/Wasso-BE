from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Club, UserClub
from .serializers import UserClubSerializer

# Create your views here.

class ClubListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """사용자가 속한 클럽들을 조회"""
        user_clubs = UserClub.objects.filter(user=request.user)
        serializer = UserClubSerializer(user_clubs, many=True)
        print(serializer.data)
        return Response({"data": serializer.data})