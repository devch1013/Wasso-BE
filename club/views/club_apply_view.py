from rest_framework import status

# from club.serializers import ClubApplySerializer
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from club.models import ClubApply
from userapp.permissions import IsAuthenticatedCustom


class ClubApplyViewSet(ModelViewSet):
    permission_classes = [IsAuthenticatedCustom]
    # serializer_class = ClubApplySerializer
    queryset = ClubApply.objects.all()

    def create(self, request, *args, **kwargs):
        club_id = request.query_params.get("club_code")
        print(club_id)
        return Response(
            {"message": "Club apply created successfully"},
            status=status.HTTP_201_CREATED,
        )
