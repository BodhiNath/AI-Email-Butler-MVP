# AI Email Butler MVP

An AI-powered email automation application with a Flutter frontend and FastAPI backend.

## Project Structure

- **`ai_email_butler/`** - Flutter cross-platform client (Android, iOS, Windows, Linux, macOS)
- **`backend/`** - FastAPI serverless backend with OpenAI integration
- **`project_design.md`** - Comprehensive project design documentation

## Quick Start

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment variables:
   ```bash
   cp .env.example .env
   # Edit .env and add your OPENAI_API_KEY
   ```

5. Run the backend:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```

### Frontend Setup

1. Navigate to the Flutter app directory:
   ```bash
   cd ai_email_butler
   ```

2. Get dependencies:
   ```bash
   flutter pub get
   ```

3. Run the app:
   ```bash
   flutter run
   ```

## Security

This repository follows security best practices:

- **Sensitive files are excluded from version control**: `.env` files, API keys, browser data, and virtual environments are listed in `.gitignore`
- **Environment variable templates**: `.env.example` files are provided to show required configuration without exposing secrets
- **Security policy**: See [SECURITY.md](SECURITY.md) for our security policy and vulnerability reporting process

### Important: Never commit sensitive data

Before committing changes, ensure you haven't accidentally included:
- API keys or tokens
- `.env` files with real credentials
- Virtual environment directories (`venv/`, `node_modules/`, etc.)
- Browser data or cache files
- Personal configuration files

## Documentation

- [Backend README](backend/README.md)
- [Frontend README](ai_email_butler/README.md)
- [Project Design](project_design.md)
- [Security Policy](SECURITY.md)

## License

This project is currently private. All rights reserved.
