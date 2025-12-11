import logging
import os
import json

from rest_framework import status
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework.decorators import action

from pydantic import BaseModel
from typing import List, Literal
from pydantic_ai import Agent
from pydantic_ai.settings import ModelSettings
from google import genai
from google.genai import types

logger = logging.getLogger(__name__)


class DamageInspectionView(ViewSet):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        logger.info("Initializing DamageInspectionView with Gemini model")
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

    @action(detail=False, methods=['post'], url_path='damage_inspection_fast')
    def damage_inspection_fast(self, request):
        logger.info("Received damage inspection fast request")

        if 'image' not in request.FILES:
            logger.warning("No image provided in request")
            return Response(
                {'error': 'No image provided'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            image = request.FILES['image']
            logger.info(f"Processing image (fast): {image.name}, size: {image.size} bytes")
            image_bytes = image.read()

            inspector_fast = DamageInspector(model_type='gemini', model_name='gemini-2.5-flash')
            result = inspector_fast.analyze_image_sync(image_bytes)

            logger.info(f"Analysis complete (fast), found {len(result['damage_areas'])} damage areas")
            return Response({
                'status': 'success',
                'filename': image.name,
                'size': image.size,
                'damage_areas': result['damage_areas']
            })

        except Exception as e:
            logger.error(f"Error processing image (fast): {str(e)}", exc_info=True)
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'], url_path='damage_inspection_v2')
    def damage_inspection_v2(self, request):
        logger.info("Received damage inspection v2 request")

        if 'image' not in request.FILES:
            logger.warning("No image provided in request")
            return Response(
                {'error': 'No image provided'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            image = request.FILES['image']
            logger.info(f"Processing image (v2): {image.name}, size: {image.size} bytes")
            image_bytes = image.read()

            PROMPT_TEXT = """
Role:
You are an expert AI Vehicle Damage Assessor. Your task is to analyze images of vehicles to identify physical damage, localize it using bounding boxes, and classify it according to a strict taxonomy.
Your analysis must be precise, damages must not be missed, even minor damages or uncertain damages should be reported. It is a lot better to thorough and over-report than under-report. Look for maximal number of possible damages and smallest possible boxes.
Verify results carefully before outputting. All damage rectangles should belong to a car part, and not reside in empty space, pavement, etc.
Objective:
Analyze the provided image. For every distinct area of damage found:
Identify:
Determine the specific car part (using snake_case naming).
Classify:
Assign the correct Damage Code from the allowed list.
Localize:
Estimate a bounding box for the damage using normalized coordinates (0.0 to 1.0).
Allowed Classification Schema (Damage Types) - Use ONLY these codes:
Other
Multiple Scratches
Torn
Stained
Soiled
Scratched
Rusted
Rubbed
Paint
Pitted
Missing
Loose
Gouged
Foreign
Faded
Dented
Cracked
Cut
Broken
Buffer
Bent

Add severity levels to the codes as follows:
- MINOR
- MEDIUM
- SEVERE

Add human readable location of the damage if possible: front_bumper, rear_bumper, left_headlight, etc.
If not possible, use "unknown_location".

Add text human readable description of the damage for each detected area.
Output Format Rules:
Output strictly valid JSON. Do not include markdown formatting (like ```json) or conversational text.
Naming Convention: For the "name" field, use descriptive snake_case (e.g., front_left_door, rear_bumper, hood).
Coordinates: The "rectangle" values must be normalized floats between 0.0 and 1.0 relative to the image width and height.
x: 0.0 is the left edge, 1.0 is the right edge.
y: 0.0 is the bottom edge, 1.0 is the top edge.
JSON Structure:Use the following structure exactly:
[{
        "damage_type": "CODE",
        "box_2d": [x1, y1, x2, y2],
        "description": "Human readable description of the damage.",
        "location": "CAR_PART",
        "severity": "SEVERITY_LEVEL"
}
]
"""

            client = genai.Client(api_key=os.getenv('GOOGLE_API_KEY'))
            MODEL_ID = "gemini-3-pro-preview"

            response = client.models.generate_content(
                model=MODEL_ID,
                contents=[
                    types.Content(
                        role="user",
                        parts=[
                            types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg"),
                            types.Part.from_text(text=PROMPT_TEXT),
                        ],
                    )
                ],
                config=types.GenerateContentConfig(
                    thinking_config=types.ThinkingConfig(
                        include_thoughts=False
                    ),
                    response_mime_type="application/json",
                ),
            )

            json_output = json.loads(response.text)

            logger.info(f"Analysis complete (v2), found {len(json_output)} damage areas")
            return Response({
                'status': 'success',
                'filename': image.name,
                'size': image.size,
                'damage_areas': json_output
            })

        except Exception as e:
            logger.error(f"Error processing image (v2): {str(e)}", exc_info=True)
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'], url_path='damage_inspection_v3')
    def damage_inspection_v3(self, request):
        logger.info("Received damage inspection v3 request")

        if 'image' not in request.FILES:
            logger.warning("No image provided in request")
            return Response(
                {'error': 'No image provided'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            image = request.FILES['image']
            logger.info(f"Processing image (v3): {image.name}, size: {image.size} bytes")
            image_bytes = image.read()

            PROMPT_TEXT = """
### Task
Find me the bounding boxes of all damages to the car in the image, classify the damage type, location and severity level.
Return a bounding box for each damage using standard normalized coordinates (0 to 1000). Cracks, dents, bents, paint chips, scratches, etc all qualifies as damage.

### Damage Type classification
Allowed Classification Schema (Damage Types) - Use ONLY these codes:
Torn
Stained
Scratched
Rusted
Paint
Missing
Dented
Cracked
Broken
Bent

### Location
Human readable description of the car part - e.g. front bumper

### Severity Level
minor, medium, severe

### Output Format Rules
Output strictly valid JSON. Do not include markdown formatting (like ```json) or conversational text.
Naming Convention: For the "name" field, use descriptive snake_case (e.g., front_left_door, rear_bumper, hood).
JSON Structure:Use the following structure exactly:
[{
        "damage_type": "CODE",
        "box_2d": [ymin, xmin, ymax, xmax],
        "description": "Human readable description of the damage.",
        "location": "CAR_PART",
        "severity": "SEVERITY_LEVEL"
}
]
"""

            client = genai.Client(api_key=os.getenv('GOOGLE_API_KEY'))
            MODEL_ID = "gemini-3-pro-preview"

            response = client.models.generate_content(
                model=MODEL_ID,
                contents=[
                    types.Content(
                        role="user",
                        parts=[
                            types.Part.from_bytes(
                                data=image_bytes,
                                mime_type="image/jpeg",
                            ),
                            types.Part.from_text(text=PROMPT_TEXT),
                        ],
                    )
                ],
                config=types.GenerateContentConfig(
                    thinking_config=types.ThinkingConfig(include_thoughts=False),
                    response_mime_type="application/json",
                ),
            )

            json_output = json.loads(response.text)

            logger.info(f"Analysis complete (v3), found {len(json_output)} damage areas")
            return Response({
                'status': 'success',
                'filename': image.name,
                'size': image.size,
                'damage_areas': json_output
            })

        except Exception as e:
            logger.error(f"Error processing image (v3): {str(e)}", exc_info=True)
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class Point(BaseModel):
    x: float
    y: float


class Rectangle(BaseModel):
    bottom_left: Point
    top_right: Point


class DamageDetection(BaseModel):
    name: str
    description: str
    severity: str
    damage_type: Literal[
        "O", "MS", "T", "ST", "SL", "S", "RU", "R", "PC", "P",
        "M", "L", "G", "FF", "F", "D", "CR", "C", "BR", "BB", "B"
    ]
    rectangle: Rectangle



class DamageInspector:
    def __init__(
        self,
        model_type: Literal['gemini', 'claude'] = 'gemini',
        google_api_key: str = None,
        anthropic_api_key: str = None,
        model_name: str = None
    ):
        self.model_type = model_type
        self.google_api_key = google_api_key or os.getenv('GOOGLE_API_KEY')
        self.anthropic_api_key = anthropic_api_key or os.getenv('ANTHROPIC_API_KEY')

        system_prompt = """Role: You are an expert AI Vehicle Damage Assessor. Your task is to analyze images of vehicles to identify physical damage, localize it using bounding boxes, and classify it according to a strict taxonomy.

Objective: Analyze the provided image. For every distinct area of damage found:
- Identify: Determine the specific car part (using snake_case naming).
- Describe: Provide a brief description of the damage (e.g., "Deep scratch along door panel", "Small dent on bumper").
- Assess Severity: Rate the damage severity (e.g., "minor", "moderate", "severe", "critical").
- Classify: Assign the correct Damage Code from the allowed list.
- Localize: Estimate a bounding box for the damage using normalized coordinates (0.0 to 1.0).

Allowed Classification Schema (Damage Types): Use ONLY these codes:
- O: Other
- MS: Multiple Scratches
- T: Torn
- ST: Stained
- SL: Soiled
- S: Scratched
- RU: Rusted
- R: Rubbed
- PC: Paint
- P: Pitted
- M: Missing
- L: Loose
- G: Gouged
- FF: Foreign
- F: Faded
- D: Dented
- CR: Cracked
- C: Cut
- BR: Broken
- BB: Buffer
- B: Bent

Output Format Rules:
- Naming Convention: For the "name" field, use descriptive snake_case (e.g., front_left_door, rear_bumper, hood).
- Description: Provide a clear, concise description of the damage. If uncertain, provide your best assessment.
- Severity: Must be one of: "minor", "moderate", "severe", or "critical". If uncertain, provide your best estimate based on visible damage.
- Coordinates: The "rectangle" values must be normalized floats between 0.0 and 1.0 relative to the image width and height.
  - x: 0.0 is the left edge, 1.0 is the right edge.
  - y: 0.0 is the bottom edge, 1.0 is the top edge.
- Return a structured list of all detected damages with name, description, severity, damage_type, and rectangle fields."""

        if model_name:
            model_name = model_name
        elif self.model_type == 'gemini':
            model_name = 'gemini-3-pro-preview'
        elif self.model_type == 'claude':
            model_name = 'claude-opus-4-5'
        else:
            raise ValueError(f"Invalid model_type: {self.model_type}")

        self.agent = Agent(
            model_name,
            output_type=List[DamageDetection],
            system_prompt=system_prompt,
            model_settings=ModelSettings(temperature=1.0)
        )

    def analyze_image_sync(self, image_data: bytes) -> dict:
        logger.info(f"Starting image analysis with {self.model_type} model")
        logger.info(f"Image size: {len(image_data)} bytes")

        try:
            result = self.agent.run_sync(
                "Analyze this car image for damages.",
                message_history=[],
            )

            logger.info(f"Agent result type: {type(result)}")
            logger.info(f"Agent result attributes: {dir(result)}")
            logger.info(f"Agent result: {result}")

            data = result.output
            logger.info(f"Extracted data type: {type(data)}")
            logger.info(f"Extracted data: {data}")

            damage_areas = []
            for detection in data:
                logger.info(f"Processing detection: {detection}")
                damage_areas.append({
                    "name": detection.name,
                    "description": detection.description,
                    "severity": detection.severity,
                    "damage_type": detection.damage_type,
                    "rectangle": {
                        "bottom_left": {
                            "x": detection.rectangle.bottom_left.x,
                            "y": detection.rectangle.bottom_left.y
                        },
                        "top_right": {
                            "x": detection.rectangle.top_right.x,
                            "y": detection.rectangle.top_right.y
                        }
                    }
                })

            logger.info(f"Successfully processed {len(damage_areas)} damage areas")
            return {"damage_areas": damage_areas}

        except Exception as e:
            logger.error(f"Error during image analysis: {str(e)}", exc_info=True)
            raise
