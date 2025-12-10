import logging
from rest_framework import status
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework.decorators import action

logger = logging.getLogger(__name__)


class DamageInspectionView(ViewSet):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        logger.info("Initializing DamageInspectionView with Gemini model")
        from damage_inspection.inspector import DamageInspector
        self.inspector = DamageInspector(model_type='gemini')

    @action(detail=False, methods=['post'])
    def damage_inspection(self, request):
        logger.info("Received damage inspection request")

        if 'image' not in request.FILES:
            logger.warning("No image provided in request")
            return Response(
                {'error': 'No image provided'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            image = request.FILES['image']
            logger.info(f"Processing image: {image.name}, size: {image.size} bytes")
            image_bytes = image.read()

            result = self.inspector.analyze_image_sync(image_bytes)

            logger.info(f"Analysis complete, found {len(result['damage_areas'])} damage areas")
            return Response({
                'status': 'success',
                'filename': image.name,
                'size': image.size,
                'damage_areas': result['damage_areas']
            })

        except Exception as e:
            logger.error(f"Error processing image: {str(e)}", exc_info=True)
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
