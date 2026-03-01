# FLIR Cattle Health Monitoring - Backend

**Python Flask REST API for cattle health diagnosis**

---

## 🚀 Quick Start

### 1. Start Server
```bash
.venv\Scripts\python backend\app.py
```

Server will run on: http://localhost:5000

### 2. Test API
```bash
.venv\Scripts\python backend\test_api.py
```

### 3. Check Health
```bash
curl http://localhost:5000/health
```

---

## 📁 Project Structure

```
backend/
├── app.py                 # Main Flask application
├── config.py              # Configuration settings
├── schemas.py             # Response data models
├── flir_parser.py         # FLIR thermal data parser
├── requirements.txt       # Python dependencies
│
├── API.md                 # API documentation
├── README.md              # This file
├── DAY1_COMPLETE.md       # Day 1 completion report
│
├── test_api.py            # Comprehensive test suite
├── test_upload.py         # Simple upload test
│
├── uploads/               # Uploaded images
├── results/               # Analysis results
└── cattle_health.db       # SQLite database (Day 3)
```

---

## 📡 API Endpoints

### Health Check
```http
GET /health
```

### Upload & Analyze Image
```http
POST /api/analyze
Content-Type: multipart/form-data

Parameters:
- image: File (required)
- animal_id: String (optional)
- thermal_data: JSON (optional)
```

**See `API.md` for complete documentation**

---

## 🧪 Testing

### Run All Tests
```bash
.venv\Scripts\python backend\test_api.py
```

### Test Single Upload
```bash
.venv\Scripts\python backend\test_upload.py
```

### Manual Test with Python
```python
import requests

files = {'image': open('../input/cow1.jpg', 'rb')}
data = {'animal_id': 'COW001'}

response = requests.post(
    'http://localhost:5000/api/analyze',
    files=files,
    data=data
)

print(response.json())
```

---

## ⚙️ Configuration

Edit `config.py` to change:
- Upload folder location
- Result folder location
- Database path
- Max file size
- Allowed file extensions
- CORS settings
- Grounding DINO model
- Temperature ranges

---

## 📦 Dependencies

### Installed
- Flask 3.1.3
- flask-cors 6.0.2
- Flask-SQLAlchemy 3.1.1
- python-dotenv 1.2.1

### Using from .venv
- transformers (Grounding DINO)
- torch (PyTorch)
- opencv-python (Image processing)
- Pillow (Image handling)
- numpy (Array operations)

---

## 🔄 Development Status

### ✅ Day 1 - Complete
- Flask server setup
- Image upload endpoint
- CORS configuration
- API documentation
- Test suite

### 🔄 Day 2 - In Progress
- Grounding DINO integration
- Body part detection
- Annotated image generation

### ⏳ Day 3 - Planned
- Database setup
- Temperature analysis
- Health diagnosis engine

### ⏳ Day 4 - Planned
- Frontend-backend connection
- History endpoints
- Animal management

### ⏳ Day 5 - Planned
- End-to-end testing
- Deployment
- Documentation

---

## 🐛 Troubleshooting

### Server won't start
```bash
# Check if port 5000 is in use
netstat -ano | findstr :5000

# Use different port in config.py
```

### Import errors
```bash
# Make sure you're using the correct venv
.venv\Scripts\activate

# Install missing packages
pip install -r requirements.txt
```

### CORS errors
```bash
# Check CORS_ORIGINS in config.py
# Make sure flask-cors is installed
```

---

## 📚 Documentation

- **API.md** - Complete API documentation
- **DAY1_COMPLETE.md** - Day 1 completion report
- **../PROJECT_TIMELINE.md** - Full project timeline

---

## 🎯 Next Steps

1. **Day 2:** Integrate Grounding DINO for body part detection
2. **Day 3:** Add database and diagnosis engine
3. **Day 4:** Connect with Android frontend
4. **Day 5:** Test and deploy

---

## 📞 Support

For issues or questions:
1. Check API.md for endpoint documentation
2. Run test_api.py to verify setup
3. Check server logs for errors

---

**Status:** Day 1 Complete ✅  
**Last Updated:** March 1, 2026

