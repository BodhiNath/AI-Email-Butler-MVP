# Quick Reference Guide - AI Email Butler

## 🚀 Getting Started (5 minutes)

### Backend Quickstart
```bash
cd backend
python3.11 -m venv venv
source venv/bin/activate  # or: venv\Scripts\activate on Windows
pip install -r requirements.txt
cp .env.example .env
# Edit .env and add OPENAI_API_KEY
uvicorn main:app --reload
```
Backend running at: http://localhost:8000

### Frontend Quickstart
```bash
cd ai_email_butler
flutter pub get
cp .env.example .env
# API_BASE_URL should be http://localhost:8000
flutter run
```

---

## 📖 Common Tasks

### Running Tests

#### Backend Tests
```bash
# All tests
pytest backend/test_main.py -v

# With coverage
pytest backend/test_main.py -v --cov=. --cov-report=html

# Specific test
pytest backend/test_main.py::TestEmailContextValidation -v
```

#### Frontend Tests
```bash
# All tests
flutter test

# With coverage
flutter test --coverage

# Specific test
flutter test test/widget_test.dart
```

### Building for Production

#### Backend Deployment
```bash
# AWS Lambda
pip install -r requirements.txt -t package/
cp main.py package/
cd package && zip -r ../deployment.zip .

# Docker
docker build -t ai-email-butler-backend .
docker run -p 8000:8000 -e OPENAI_API_KEY=sk-xxx ai-email-butler-backend
```

#### Frontend Build
```bash
# Android
flutter build apk --release

# iOS
flutter build ios --release

# Web
flutter build web

# Desktop
flutter build linux  # or windows, macos
```

---

## 🔑 API Authentication

### Generate JWT Token
```python
import jwt
import json
from datetime import datetime, timedelta

secret = "your-jwt-secret"
payload = {
    "sub": "user_id",
    "iat": datetime.utcnow(),
    "exp": datetime.utcnow() + timedelta(hours=24)
}
token = jwt.encode(payload, secret, algorithm="HS256")
print(f"Token: {token}")
```

### Use JWT in Requests
```bash
# cURL example
curl -X POST http://localhost:8000/api/v1/ai/suggest-action \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "subject": "Test",
    "body": "Test body",
    "sender": "test@example.com",
    "user_id": "user123",
    "workflow_rules": "Auto-reply"
  }'
```

### Use in Flutter
```dart
final apiService = ApiService(
  jwtToken: 'your_jwt_token',
  userId: 'user_id',
);
final suggestion = await apiService.suggestAction(emailContext);
```

---

## 🐛 Troubleshooting

### Backend Issues

#### "OPENAI_API_KEY not found"
```bash
# Check .env file exists
ls -la backend/.env

# Add your API key
echo "OPENAI_API_KEY=sk-xxx" >> backend/.env
```

#### "Invalid token" errors
- Ensure JWT token is properly formatted: `Bearer <token>`
- Verify token is not expired
- Check JWT_SECRET in backend .env matches

#### Rate limit errors (429)
- Default: 5 requests/minute per IP
- Wait 1-2 minutes before retrying

### Frontend Issues

#### "Connection refused"
- Backend must be running: `uvicorn main:app --reload`
- Check API_BASE_URL in .env: should be `http://localhost:8000`

#### "Invalid token" in Flutter
- Generate valid JWT token from backend
- Verify token hasn't expired
- Check token is passed correctly to ApiService

#### Hot reload not working
```bash
flutter clean
flutter pub get
flutter run
```

---

## 📊 API Endpoints

| Method | Endpoint | Auth | Rate Limit | Description |
|--------|----------|------|-----------|-------------|
| GET | `/` | No | No | Health check |
| GET | `/api/v1/user/status?user_id=X` | Yes | No | User subscription status |
| POST | `/api/v1/ai/suggest-action` | Yes | Yes (5/min) | Get AI action suggestion |
| POST | `/api/v1/accounts/add` | Yes | No | Add OAuth account |
| POST | `/api/v1/workflows/sync` | Yes | No | Sync workflows |
| POST | `/api/v1/actions/log` | Yes | No | Log actions |

---

## 🔒 Security Checklist

- ✅ JWT tokens for all protected endpoints
- ✅ Rate limiting on sensitive endpoints
- ✅ Input validation on all fields
- ✅ User authorization checks
- ✅ Environment variables for secrets
- ✅ HTTPS in production
- ✅ Structured logging for audits
- ✅ No hardcoded credentials

---

## 📱 Supported Platforms

- ✅ Android (APK/AAB)
- ✅ iOS (IPA)
- ✅ Web (Flutter Web)
- ✅ Linux (Desktop)
- ✅ Windows (Desktop)
- ✅ macOS (Desktop)

---

## 🔄 Environment Variables

### Backend (.env)
```env
OPENAI_API_KEY=sk-your-key
JWT_SECRET=your-secret-min-32-chars
OPENAI_API_BASE=https://api.openai.com/v1  # Optional
API_KEY_HEADER=X-API-Key  # Optional
```

### Frontend (.env)
```env
API_BASE_URL=http://localhost:8000
DEBUG_MODE=true
```

---

## 📚 Documentation Files

| File | Purpose |
|------|---------|
| `project_design.md` | Architecture and schema design |
| `backend/README.md` | Backend setup and deployment |
| `ai_email_butler/README.md` | Frontend setup and usage |
| `IMPLEMENTATION_SUMMARY.md` | All changes summary |
| `CHANGELOG.md` | Detailed changelog |
| `QUICK_REFERENCE.md` | This file |

---

## 🧪 Test Commands

```bash
# Backend unit tests
pytest backend/test_main.py -v

# Backend with coverage
pytest backend/test_main.py --cov=. --cov-report=html

# Frontend widget tests
flutter test

# Frontend with coverage
flutter test --coverage

# Lint checks
flake8 backend/main.py  # Backend
flutter analyze  # Frontend

# Format code
flutter format lib/  # Frontend
black backend/main.py  # Backend
```

---

## 🎯 Example Workflow

### 1. Start Backend
```bash
cd backend
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Add OPENAI_API_KEY to .env
uvicorn main:app --reload
```

### 2. Get JWT Token
```bash
python3 -c "
import jwt
from datetime import datetime, timedelta

secret = 'dev-secret-key-change-in-production'
token = jwt.encode(
    {'sub': 'user123', 'exp': datetime.utcnow() + timedelta(hours=1)},
    secret,
    algorithm='HS256'
)
print(token)
"
```

### 3. Test API (cURL)
```bash
TOKEN="your-token-here"
curl -X POST http://localhost:8000/api/v1/ai/suggest-action \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "subject": "Follow up",
    "body": "Can you send the report?",
    "sender": "boss@company.com",
    "user_id": "user123",
    "workflow_rules": "Draft reply"
  }'
```

### 4. Run Flutter App
```bash
cd ai_email_butler
flutter pub get
# Update .env with API_BASE_URL and JWT token
flutter run
```

---

## 🚀 Deployment Checklist

### Before Production
- [ ] Update JWT_SECRET to strong random value
- [ ] Set OPENAI_API_KEY securely
- [ ] Enable HTTPS/TLS
- [ ] Set up CI/CD pipelines
- [ ] Run full test suite
- [ ] Configure rate limits appropriately
- [ ] Set up logging and monitoring
- [ ] Document API endpoints
- [ ] Train team on security practices
- [ ] Set up backup and recovery

### Environment Variables (Production)
```env
# Backend
OPENAI_API_KEY=sk-prod-xxx
JWT_SECRET=super-secret-32-char-minimum
OPENAI_API_BASE=https://api.openai.com/v1

# Frontend
API_BASE_URL=https://api.email-butler.com
DEBUG_MODE=false
```

---

## 📞 Support Resources

- **Flutter Docs:** https://flutter.dev/docs
- **FastAPI Docs:** https://fastapi.tiangolo.com/
- **OpenAI API:** https://platform.openai.com/docs
- **JWT:** https://jwt.io/
- **Local API Docs:** http://localhost:8000/docs

---

**Last Updated:** November 15, 2025  
**Version:** 1.0.0-MVP
