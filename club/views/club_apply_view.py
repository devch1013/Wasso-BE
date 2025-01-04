from rest_framework import status

# from club.serializers import ClubApplySerializer
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from club.models import ClubApply, Generation
from main.exceptions import CustomException, ErrorCode
from userapp.permissions import IsAuthenticatedCustom


class ClubApplyViewSet(ModelViewSet):
    permission_classes = [IsAuthenticatedCustom]
    # serializer_class = ClubApplySerializer
    queryset = ClubApply.objects.all()

    def create(self, request, *args, **kwargs):
        club_code = request.query_params.get("club-code")
        if not club_code:
            raise CustomException(ErrorCode.PARAMS_MISSING)
        generation = Generation.objects.filter(invite_code=club_code).first()
        if not generation:
            raise CustomException(ErrorCode.GENERATION_NOT_FOUND)
        ClubApply.objects.create(user=request.user, club=generation.club)
        return Response(
            {"message": "Club apply created successfully"},
            status=status.HTTP_201_CREATED,
        )
