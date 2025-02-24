from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from api.club.models import ClubApply, Generation, GenMember
from api.event.models import Event
from api.event.serializers.event_serializer import EventSerializer
from api.club.serializers.club_apply_serializers import ClubApplySerializer
from api.club.serializers.member_serializers import (
    GenerationMappingSerializer,
)
from api.club.serializers.generation_serializers import GenerationStatsSerializer
from api.club.services.generation_service import GenerationService
from common.utils.google_sheet import create_attendance_sheet
from common.utils.notion import NotionAttendanceManager
from common.utils.excel import create_attendance_excel
class GenerationView(ModelViewSet):
    queryset = Generation.objects.all()

    def get_serializer_class(self):
        if self.action == "apply":
            return ClubApplySerializer
        return None

    @action(detail=True, methods=["get"])
    def apply(self, request, *args, **kwargs):
        """Club으로 옮겨야함"""
        applies = ClubApply.objects.filter(generation=self.get_object(), accepted=False)
        serializer = self.get_serializer(applies, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["get"])
    def members(self, request, *args, **kwargs):
        """기수별 회원 정보"""
        members = GenMember.objects.filter(generation=self.get_object()).order_by("member__user__username")
        serializer = GenerationMappingSerializer(members, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=["get"])
    def events(self, request, *args, **kwargs):
        """기수별 이벤트 정보"""
        events = Event.objects.filter(generation=self.get_object()).order_by("date")
        serializer = EventSerializer(events, context={"user": request.user}, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=["get"])
    def stats(self, request, *args, **kwargs):
        """기수 출석 통계"""
        generation = self.get_object()
        
        # Get all generation mappings and their members
        stats = GenerationService.get_generation_stats(generation.id)
        serializer = GenerationStatsSerializer(stats, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=["get"], url_path="stats/google-sheet")
    def google_sheet(self, request, *args, **kwargs):
        """구글 시트 연동"""
        generation = self.get_object()
        url = create_attendance_sheet(generation.id)
        return Response({"url": url}, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=["get"], url_path="stats/notion")
    def notion(self, request, *args, **kwargs):
        """노션 연동"""
        generation = self.get_object()
        notion_db = NotionAttendanceManager(notion_parent_page_id="1a37549e7ac480a8b877fbee5e16ad33")
        notion_db.update_attendance_database(generation.id, database_id="1a37549e7ac480baaa62cd7bd819b510")
        return Response({"url": "url"}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["get"], url_path="stats/excel")
    def excel(self, request, *args, **kwargs):
        """엑셀 연동"""
        generation = self.get_object()
        file_path = create_attendance_excel(generation.id)
        return Response({"url": file_path}, status=status.HTTP_200_OK)
