import os
import logging
from typing import List, Literal, Optional
from pydantic_ai import Agent
from .models import DamageDetection

logger = logging.getLogger(__name__)


class DamageInspector:
    def __init__(
        self,
        model_type: Literal['gemini', 'claude'] = 'gemini',
        google_api_key: str = None,
        anthropic_api_key: str = None
    ):
        self.model_type = model_type
        self.google_api_key = google_api_key or os.getenv('GOOGLE_API_KEY')
        self.anthropic_api_key = anthropic_api_key or os.getenv('ANTHROPIC_API_KEY')

        system_prompt = """Role: You are an expert AI Vehicle Damage Assessor. Your task is to analyze images of vehicles to identify physical damage, localize it using bounding boxes, and classify it according to a strict taxonomy.

Objective: Analyze the provided image. For every distinct area of damage found:
- Identify: Determine the specific car part (using snake_case naming).
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
- Coordinates: The "rectangle" values must be normalized floats between 0.0 and 1.0 relative to the image width and height.
  - x: 0.0 is the left edge, 1.0 is the right edge.
  - y: 0.0 is the bottom edge, 1.0 is the top edge.
- Return a structured list of all detected damages with name, damage_type, and rectangle fields."""

        if self.model_type == 'gemini':
            model_name = 'gemini-3-pro-preview'
        elif self.model_type == 'claude':
            model_name = 'claude-opus-4-5'
        else:
            raise ValueError(f"Invalid model_type: {self.model_type}")

        self.agent = Agent(
            model_name,
            output_type=List[DamageDetection],
            system_prompt=system_prompt
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
