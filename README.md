# Backend API

Flask backend for the AI Feedback System.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create `.env` file:
```bash
cp .env.example .env
```

3. Set environment variables:
- `GEMINI_API_KEY` or `OPENROUTER_API_KEY`
- `DATABASE_URL` (defaults to SQLite)
- `CORS_ORIGINS` (comma-separated list of allowed origins)

4. Run the server:
```bash
python app.py
```

Or with gunicorn:
```bash
gunicorn app:app --bind 0.0.0.0:5000
```

## API Endpoints

- `GET /health` - Health check
- `POST /api/submit-review` - Submit a new review
- `GET /api/admin/reviews` - Get all reviews (admin)
- `GET /api/admin/reviews/<review_id>` - Get specific review

## Deployment

### Render
1. Connect your GitHub repository
2. Set build command: `pip install -r requirements.txt`
3. Set start command: `gunicorn app:app --bind 0.0.0.0:$PORT`
4. Add environment variables in Render dashboard

### Other Platforms
The `Procfile` is configured for Heroku/Render. Adjust as needed for your platform.


