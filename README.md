# Cattle Health Monitoring - Backend API

Flask backend for cattle health monitoring system using FLIR thermal cameras.

## Features

- 🐄 Cattle body part detection via HuggingFace Space (Grounding DINO)
- 🌡️ Temperature analysis and health diagnosis
- 📊 PostgreSQL database for scan history
- 🔄 RESTful API for Android app integration
- 🚀 Lightweight deployment (no heavy ML dependencies)

---

## Architecture

```
Android App → Backend API → HuggingFace Space (AI Detection)
                ↓
          PostgreSQL Database
```

---

## Local Development

### Prerequisites

- Python 3.11+
- pip

### Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
cp .env.example .env
# Edit .env with your HuggingFace Space username

# Run server
python app.py
```

Server runs on `http://localhost:5000`

### Test

```bash
# Test HuggingFace Space connection
python test_space_client.py

# Test complete workflow
python test_local_complete.py
```

---

## Production Deployment (Render)

### Prerequisites

- Render account
- HuggingFace Space deployed
- PostgreSQL database on Render

### Deploy

1. Create PostgreSQL database on Render
2. Create Web Service on Render
3. Set environment variables:
   ```
   HF_SPACE_USERNAME=your_username
   HF_SPACE_NAME=cattle-detection-api
   FLASK_ENV=production
   DATABASE_URL=<your_postgres_url>
   ```
4. Deploy!

See `../RENDER_DEPLOYMENT.md` for detailed instructions.

---

## API Endpoints

### Health Check
```
GET /health
```

### Analyze Image
```
POST /api/analyze
Content-Type: multipart/form-data

Parameters:
- image: Image file
- animal_id: Animal ID (optional)

Returns: Scan ID, detections, body parts
```

### Diagnose
```
POST /api/diagnose
Content-Type: application/json

Body:
{
  "scan_id": "uuid",
  "temperatures": {
    "head": {"mean": 38.5, "max": 39.0, "min": 38.0, "std": 0.3},
    ...
  }
}

Returns: Health status, alerts, recommendations
```

See `API.md` for complete API documentation.

---

## Database Schema

- **animals**: Animal information
- **scans**: Scan records
- **detections**: Body part detections
- **temperatures**: Temperature readings
- **diagnoses**: Health diagnoses

Tables are created automatically on first run.

---

## Environment Variables

### Required

- `HF_SPACE_USERNAME`: Your HuggingFace username
- `HF_SPACE_NAME`: Your Space name (default: cattle-detection-api)

### Optional

- `DATABASE_URL`: PostgreSQL connection string (auto-detected on Render)
- `FLASK_ENV`: Environment (development/production)

---

## File Structure

```
backend/
├── app.py                  # Main Flask application
├── config.py               # Configuration
├── database.py             # Database models
├── schemas.py              # Response schemas
├── flir_parser.py          # FLIR data parser
├── services/
│   ├── detection_service_hf_space.py  # HF Space client
│   ├── diagnosis_service.py           # Health diagnosis
│   └── visualization_service.py       # Image annotation
├── requirements.txt        # Local dependencies
├── requirements-render.txt # Production dependencies
├── test_space_client.py    # Test HF Space
└── test_local_complete.py  # Test complete workflow
```

---

## Dependencies

### Local (requirements.txt)
- Full ML stack (torch, transformers) for local testing
- ~3GB total

### Production (requirements-render.txt)
- Lightweight (no ML dependencies)
- Uses HuggingFace Space for AI
- ~50MB total

---

## Performance

| Scenario | Time |
|----------|------|
| First request (cold start) | 60-90s |
| Subsequent requests | 5-10s |
| With GPU Space | 2-5s |

---

## Troubleshooting

### Space Connection Error
- Check HF_SPACE_USERNAME is correct
- Verify Space is running
- Install gradio_client: `pip install gradio_client`

### Database Error
- Check DATABASE_URL is set
- Verify PostgreSQL is running
- Check psycopg2-binary is installed

### Import Error
- Install dependencies: `pip install -r requirements.txt`
- Check Python version: 3.11+

---

## License

Apache 2.0

---

## Support

For issues or questions, check:
- `API.md` - API documentation
- `../RENDER_DEPLOYMENT.md` - Deployment guide
- `../DATABASE_INFO.md` - Database information
