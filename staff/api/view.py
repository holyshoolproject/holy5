from rest_framework import viewsets
from ..models import StaffProfile
from .ses import StaffProfileSerializer
from rest_framework.decorators import action
from rest_framework.response import Response

class StaffProfileViewSet(viewsets.ModelViewSet):
    queryset = StaffProfile.objects.all()
    serializer_class = StaffProfileSerializer

    @action(detail=False, methods=['get'])
    def total_teachers(self, request):
        total = self.get_queryset().count()
        return Response({"total_teachers": total})
