import os
from typing import List, Literal, Optional
from pydantic_ai import Agent, ModelSettings
from pydantic_ai.models.google import GoogleModel, GoogleModelSettings
from pydantic_ai.models.anthropic import AnthropicModel, AnthropicModelSettings
from pydantic_ai.models.fallback import FallbackModel
from pydantic_ai.providers.google import GoogleProvider
from pydantic_ai.providers.anthropic import AnthropicProvider
from .models import DamageDetection


class DamageInspector:
    def __init__(
        self,
        model_type: Literal['gemini', 'claude', 'fallback'] = 'gemini',
        google_api_key: str = None,
        anthropic_api_key: str = None,
        gemini_settings: Optional[GoogleModelSettings] = None,
        claude_settings: Optional[AnthropicModelSettings] = None
    ):
        self.model_type = model_type
        self.google_api_key = google_api_key or os.getenv('GOOGLE_API_KEY')
        self.anthropic_api_key = anthropic_api_key or os.getenv('ANTHROPIC_API_KEY')

        self.gemini_settings = gemini_settings
        self.claude_settings = claude_settings

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

        model = self._create_model()

        agent_kwargs = {
            'model': model,
            'output_type': List[DamageDetection],
            'system_prompt': system_prompt
        }

        if self.agent_settings:
            agent_kwargs['model_settings'] = self.agent_settings

        self.agent = Agent(**agent_kwargs)

    def _create_model(self):
        if self.model_type == 'gemini':
            provider = GoogleProvider(api_key=self.google_api_key)
            model = GoogleModel('gemini-3.0-pro', provider=provider)
            self.agent_settings = self.gemini_settings
            return model

        elif self.model_type == 'claude':
            provider = AnthropicProvider(api_key=self.anthropic_api_key)
            model = AnthropicModel('claude-opus-4-5', provider=provider)
            self.agent_settings = self.claude_settings
            return model

        elif self.model_type == 'fallback':
            google_provider = GoogleProvider(api_key=self.google_api_key)
            google_model = GoogleModel('gemini-2.5-flash', provider=google_provider)

            anthropic_provider = AnthropicProvider(api_key=self.anthropic_api_key)
            anthropic_model = AnthropicModel('claude-opus-4-5', provider=anthropic_provider)

            self.agent_settings = None
            return FallbackModel(google_model, anthropic_model)

        else:
            raise ValueError(f"Invalid model_type: {self.model_type}")

    def analyze_image_sync(self, image_data: bytes) -> dict:
        result = self.agent.run_sync(
            "Analyze this car image for damages.",
            message_history=[],
        )

        damage_areas = []
        for detection in result.output:
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

        return {"damage_areas": damage_areas}
