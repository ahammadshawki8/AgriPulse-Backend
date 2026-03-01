# FLIR Cattle Health Monitoring - Backend API Documentation

**Version:** 1.0.0
**Base URL:** `http://localhost:5000`
**Last Updated:** March 4, 2026 (Day 3 Complete)

---

## Overview

This API provides endpoints for cattle health monitoring using FLIR thermal imaging and Grounding DINO AI detection.

### Workflow
1. **POST /api/analyze** - Upload image, get body part coordinates
2. Frontend extracts temperatures from thermal data
3. **POST /api/diagnose** - Send temperatures, get health diagnosis
4. **GET /api/scans/{id}** - View complete scan details
5. **GET /api/animals/{id}/scans** - View scan history

---

## Endpoints

### 1. Health Check

**GET** `/health`

Check if the API is running.

**Response:**
```json
{
  "status": "ok",
  "message": "FLIR Cattle Health Monitoring API is running",
  "version": "1.0.0"
}
```

---

### 2. Analyze Image (Step 1)

**POST** `/api/analyze`

Upload cattle image and run Grounding DINO detection. Returns body part coordinates for temperature extraction.

**Request:**
- Content-Type: `multipart/form-data`
- Body:
  - `image`: File (JPEG/PNG) - Required
  - `animal_id`: String - Optional
  - `thermal_data`: JSON - Optional (for future use)

**Example (curl):**
```bash
curl -X POST http://localhost:5000/api/analyze \
  -F "image=@cow1.jpg" \
  -F "animal_id=COW001"
```

**Response:**
```json
{
  "success": true,
  "scan_id": "aeef37c8-0097-48af-b463-c9e17f876b67",
  "timestamp": "2026-03-04T10:30:00",
  "animal_id": "COW001",
  "body_parts": {
    "head": [633, 131, 869, 347],
    "udder": [589, 417, 726, 503],
    "leg_1": [653, 477, 763, 650],
    "leg_2": [763, 477, 873, 650]
  },
  "detections": [
    {
      "label": "cow head",
      "confidence": 0.714,
      "bbox": [633, 131, 869, 347]
    },
    {
      "label": "cow udder",
      "confidence": 0.682,
      "bbox": [589, 417, 726, 503]
    }
  ],
  "image_path": "uploads/scan_uuid.jpg",
  "annotated_image_path": "results/annotated_uuid.jpg",
  "message": "Body parts detected successfully. Use /api/diagnose to analyze temperatures."
}
```

**Status Codes:**
- `200`: Success
- `400`: Bad request (no image, invalid file type)
- `500`: Server error

---

### 3. Diagnose Health (Step 2)

**POST** `/api/diagnose`

Analyze temperature readings and generate health diagnosis.

**Request:**
- Content-Type: `application/json`
- Body:
```json
{
  "scan_id": "aeef37c8-0097-48af-b463-c9e17f876b67",
  "temperatures": {
    "head": {
      "temp_mean": 38.2,
      "temp_max": 38.5,
      "temp_min": 37.9,
      "temp_std": 0.2
    },
    "udder": {
      "temp_mean": 38.7,
      "temp_max": 39.1,
      "temp_min": 38.3,
      "temp_std": 0.3
    },
    "leg_1": {
      "temp_mean": 37.3,
      "temp_max": 37.6,
      "temp_min": 37.0,
      "temp_std": 0.2
    }
  }
}
```

**Example (curl):**
```bash
curl -X POST http://localhost:5000/api/diagnose \
  -H "Content-Type: application/json" \
  -d '{
    "scan_id": "aeef37c8-0097-48af-b463-c9e17f876b67",
    "temperatures": {
      "head": {"temp_mean": 38.2, "temp_max": 38.5, "temp_min": 37.9, "temp_std": 0.2},
      "udder": {"temp_mean": 38.7, "temp_max": 39.1, "temp_min": 38.3, "temp_std": 0.3}
    }
  }'
```

**Response:**
```json
{
  "success": true,
  "scan_id": "aeef37c8-0097-48af-b463-c9e17f876b67",
  "diagnosis": {
    "status": "attention_needed",
    "alerts": [
      {
        "part": "udder",
        "issue": "elevated_temperature",
        "value": 38.7,
        "normal_range": [37.5, 38.5],
        "deviation": 0.2
      }
    ],
    "recommendations": [
      "Elevated udder temperature (38.7°C). Normal range: 37.5-38.5°C. Possible mastitis. Recommend veterinary examination and milk culture test."
    ]
  },
  "message": "Diagnosis completed successfully"
}
```

**Status Codes:**
- `200`: Success
- `400`: Bad request (missing scan_id or temperatures)
- `404`: Scan not found
- `500`: Server error

---

### 4. Get All Animals

**GET** `/api/animals`

Get list of all animals in the database.

**Response:**
```json
{
  "success": true,
  "animals": [
    {
      "id": "COW001",
      "tag_id": "DC-001",
      "name": "Bessie",
      "breed": "Holstein",
      "age": 3,
      "created_at": "2026-03-04T08:00:00"
    },
    {
      "id": "COW002",
      "tag_id": "DC-002",
      "name": "Daisy",
      "breed": "Jersey",
      "age": 4,
      "created_at": "2026-03-04T08:00:00"
    }
  ],
  "count": 2
}
```

---

### 5. Get Animal Scan History

**GET** `/api/animals/{animal_id}/scans`

Get all scans for a specific animal.

**Example:**
```bash
curl http://localhost:5000/api/animals/COW001/scans
```

**Response:**
```json
{
  "success": true,
  "animal_id": "COW001",
  "scans": [
    {
      "id": "aeef37c8-0097-48af-b463-c9e17f876b67",
      "animal_id": "COW001",
      "timestamp": "2026-03-04T10:30:00",
      "image_path": "uploads/scan_uuid.jpg",
      "annotated_image_path": "results/annotated_uuid.jpg"
    }
  ],
  "count": 1
}
```

---

### 6. Get Scan Details

**GET** `/api/scans/{scan_id}`

Get complete details of a specific scan including detections, temperatures, and diagnosis.

**Example:**
```bash
curl http://localhost:5000/api/scans/aeef37c8-0097-48af-b463-c9e17f876b67
```

**Response:**
```json
{
  "success": true,
  "scan": {
    "id": "aeef37c8-0097-48af-b463-c9e17f876b67",
    "animal_id": "COW001",
    "timestamp": "2026-03-04T10:30:00",
    "image_path": "uploads/scan_uuid.jpg",
    "annotated_image_path": "results/annotated_uuid.jpg",
    "detections": [
      {
        "label": "cow head",
        "confidence": 0.714,
        "bbox": [633, 131, 869, 347]
      }
    ],
    "temperatures": [
      {
        "body_part": "head",
        "temp_mean": 38.2,
        "temp_max": 38.5,
        "temp_min": 37.9,
        "temp_std": 0.2
      }
    ],
    "diagnosis": {
      "status": "healthy",
      "alerts": [],
      "recommendations": [
        "All temperature readings are within normal ranges. Animal appears healthy."
      ],
      "created_at": "2026-03-04T10:30:05"
    }
  }
}
```

**Status Codes:**
- `200`: Success
- `404`: Scan not found
- `500`: Server error

---

## Data Models

### Temperature Ranges (Celsius)

```python
head/nose/eye/ear: 37.5-38.5°C
udder: 37.5-38.5°C
leg/hoof: 37.0-38.0°C
body/neck/tail: 37.5-38.5°C
```

### Health Status

- `healthy`: All temperature readings within normal ranges
- `attention_needed`: One or more abnormalities detected

### Alert Types

- `low_temperature`: Temperature below normal range
- `elevated_temperature`: Temperature above normal range

---

## Error Responses

All error responses follow this format:

```json
{
  "error": "Error message",
  "details": "Detailed error information"
}
```

**Common Errors:**
- `400 Bad Request`: Invalid input data
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

---

## Testing

### Test with curl

1. **Health Check:**
```bash
curl http://localhost:5000/health
```

2. **Analyze Image:**
```bash
curl -X POST http://localhost:5000/api/analyze \
  -F "image=@cow1.jpg" \
  -F "animal_id=COW001"
```

3. **Diagnose:**
```bash
curl -X POST http://localhost:5000/api/diagnose \
  -H "Content-Type: application/json" \
  -d '{"scan_id":"uuid","temperatures":{"head":{"temp_mean":38.2,"temp_max":38.5,"temp_min":37.9,"temp_std":0.2}}}'
```

### Test Suite

Run the complete test suite:
```bash
cd backend
python test_day3_complete.py
```

---

## Notes

- All timestamps are in ISO 8601 format
- Image files are saved in `backend/uploads/`
- Annotated images are saved in `backend/results/`
- Database is SQLite at `backend/cattle_health.db`
- Maximum file size: 16MB
- Allowed file types: JPEG, PNG

---

**Last Updated:** March 4, 2026 (Day 3 Complete)
