# AI Damage Inspection Backend

A Django REST API backend for AI-powered vehicle damage assessment using computer vision models. This project provides endpoints for analyzing vehicle images to detect, classify, and localize damage areas using Google's Gemini AI models.

## Features

- **Image-based Damage Detection**: Upload vehicle images and receive detailed damage analysis
- **Multiple AI Models**: Support for Google Gemini (including fast and preview models)
- **Streamlined Damage Classification**: 10 core damage types with severity levels
- **Bounding Box Localization**: Precise damage area coordinates with normalized positioning (0-1000 scale in v3)
- **RESTful API**: Clean REST endpoints with proper error handling and logging
- **Multiple Analysis Modes**: Standard, fast, advanced (v2), and streamlined (v3) analysis endpoints

## Tech Stack

- **Framework**: Django 5.2.9 with Django REST Framework
- **AI/ML**: 
  - Pydantic AI 1.29.0
  - Google Generative AI (Gemini models)
  - Anthropic Claude (optional)
- **Database**: SQLite (development)
- **Python**: 3.10+

## API Endpoints

### Damage Inspection Endpoints

1. **Standard Analysis**
   ```
   POST /damage_inspection/
   ```

2. **Fast Analysis** (using Gemini 2.5 Flash)
   ```
   POST /damage_inspection_fast/
   ```

3. **Advanced Analysis v2** (using Gemini 3 Pro Preview)
   ```
   POST /damage_inspection_v2/
   ```

4. **Streamlined Analysis v3** (using Gemini 3 Pro Preview with simplified classification)
   ```
   POST /damage_inspection_v3/
   ```

All endpoints accept:
- **Content-Type**: `multipart/form-data`
- **Parameter**: `image` (image file)

### Response Format

#### v1/v2 Response Format
```json
{
  "status": "success",
  "filename": "car_image.jpg",
  "size": 2048576,
  "damage_areas": [
    {
      "name": "front_left_door",
      "description": "Deep scratch along door panel",
      "severity": "MEDIUM",
      "damage_type": "Scratched",
      "box_2d": [0.2, 0.3, 0.4, 0.6],
      "location": "front_left_door"
    }
  ]
}
```

#### v3 Response Format (Streamlined)
```json
{
  "status": "success",
  "filename": "car_image.jpg",
  "size": 2048576,
  "damage_areas": [
    {
      "damage_type": "Scratched",
      "box_2d": [100, 200, 300, 400],
      "description": "Deep scratch along door panel",
      "location": "front bumper",
      "severity": "medium"
    }
  ]
}
```

**Note**: v3 uses coordinates in 0-1000 scale format `[ymin, xmin, ymax, xmax]`

## Damage Classification

### v1/v2 Classification (21 damage types)
- **Surface**: Scratched, Multiple Scratches, Rubbed, Faded, Stained, Soiled
- **Structural**: Dented, Cracked, Broken, Bent, Torn, Cut, Gouged
- **Material**: Missing, Loose, Rusted, Pitted
- **Other**: Paint, Foreign, Buffer, Other

### v3 Classification (10 streamlined types)
- Torn
- Stained  
- Scratched
- Rusted
- Paint
- Missing
- Dented
- Cracked
- Broken
- Bent

### Severity Levels
- **v1/v2**: MINOR, MEDIUM, SEVERE
- **v3**: minor, medium, severe

## Installation & Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd hackaton-team-3-backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r ai_damage_inspection/requirements.txt
   ```

4. **Environment Configuration**
   Create a `.env` file in the `ai_damage_inspection` directory:
   ```env
   GOOGLE_API_KEY=your_google_gemini_api_key
   ANTHROPIC_API_KEY=your_anthropic_api_key  # Optional
   ```

5. **Database Setup**
   ```bash
   cd ai_damage_inspection
   python manage.py migrate
   ```

6. **Run Development Server**
   ```bash
   python manage.py runserver
   ```

The API will be available at `http://localhost:8000/`

## Usage Example

### Using curl
```bash
curl -X POST http://localhost:8000/damage_inspection/ \
  -F "image=@/path/to/car_image.jpg" \
  -H "Accept: application/json"
```

### Using Python requests
```python
import requests

url = "http://localhost:8000/damage_inspection/"
files = {"image": open("car_image.jpg", "rb")}
response = requests.post(url, files=files)
print(response.json())
```

## Project Structure

```
ai_damage_inspection/
├── ai_damage_inspection/          # Django project settings
│   ├── settings.py               # Configuration with AI model settings
│   ├── urls.py                   # URL routing
│   └── wsgi.py                   # WSGI configuration
├── app/                          # Main application
│   ├── views.py                  # API endpoints and AI integration
│   └── models.py                 # Database models (currently empty)
├── manage.py                     # Django management script
├── requirements.txt              # Python dependencies
└── db.sqlite3                    # SQLite database
```

## Configuration

### Model Settings
- **Default Model**: Gemini 3 Pro Preview
- **Fast Model**: Gemini 2.5 Flash
- **Temperature**: 1.0 (configurable in ModelSettings)
- **Output Format**: Structured JSON with Pydantic validation

### Logging
Comprehensive logging is configured for:
- Request processing
- Image analysis
- Error handling
- Performance monitoring

## Development

### Adding New Damage Types
Modify the `damage_type` Literal in `views.py:225-228` and update the system prompts accordingly.

### Model Configuration
The `DamageInspector` class supports multiple AI providers:
- Google Gemini (default)
- Anthropic Claude

### API Versioning
New analysis endpoints can be added following the pattern in `damage_inspection_v2` and `damage_inspection_v3`. The v3 endpoint uses a simplified coordinate system (0-1000 scale) and streamlined damage classification for faster processing.

## License

This project was developed for a hackathon and is available for educational and development purposes.

## Support

For issues and feature requests, please check the project's issue tracker or contact the development team.