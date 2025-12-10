from rest_framework import status
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework.decorators import action


class DamageInspectionView(ViewSet):
    @action(detail=False, methods=['post', 'get'])
    def damage_inspection(self, request):
        if 'image' not in request.FILES:
            return Response(
                {'error': 'No image provided'},
                status=status.HTTP_400_BAD_REQUEST
            )

        image = request.FILES['image']
        return Response({
            'status': 'success',
            'filename': image.name,
            'size': image.size
        })
