from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework.decorators import action


class DamageInspectionView(ViewSet):
    @action(detail=False, methods=['post', 'get'])
    def damage_inspection(self, request):
        return Response({"message": "Damage inspection endpoint"})