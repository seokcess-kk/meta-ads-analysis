# Meta Ad Analyzer

AI-powered Meta Ad Library analysis platform. Collect ads from Meta Ad Library API and analyze images and copy using Claude AI.

## Features

- **Ad Collection**: Fetch ads from Meta Ad Library API by keywords and industry
- **AI Image Analysis**: Analyze ad images for composition, colors, layout using Claude Vision
- **AI Copy Analysis**: Analyze ad copy for structure, tone, target audience, keywords
- **Dashboard**: Browse collected ads with filtering and sorting
- **Background Processing**: Celery workers for async ad collection and analysis

## Tech Stack

### Backend
- **FastAPI** - Async Python web framework
- **SQLAlchemy** - Async ORM with PostgreSQL
- **Celery** - Distributed task queue
- **Redis** - Message broker and cache
- **Claude API** - AI analysis (claude-sonnet-4-20250514)

### Frontend
- **Next.js 14** - React framework with App Router
- **TailwindCSS** - Utility-first CSS
- **Zustand** - State management
- **SWR** - Data fetching

### Infrastructure
- **Docker Compose** - Container orchestration
- **PostgreSQL** - Primary database
- **Redis** - Queue and cache

## Quick Start

### Prerequisites
- Docker Desktop
- Meta API Access Token
- Anthropic API Key

### 1. Clone the repository
```bash
git clone https://github.com/seokcess-kk/meta-ads-analysis.git
cd meta-ads-analysis
```

### 2. Configure environment variables

**Backend** (`backend/.env`):
```env
DATABASE_URL=postgresql://postgres:postgres@db:5432/meta_ads
REDIS_URL=redis://redis:6379/0
CELERY_BROKER_URL=redis://redis:6379/1

ANTHROPIC_API_KEY=your-anthropic-api-key
META_ACCESS_TOKEN=your-meta-access-token

AWS_ACCESS_KEY_ID=your-aws-key  # Optional
AWS_SECRET_ACCESS_KEY=your-aws-secret  # Optional
S3_BUCKET_NAME=meta-ads-images  # Optional

DEBUG=true
LOG_LEVEL=INFO
CORS_ORIGINS=http://localhost:3000
```

**Frontend** (`frontend/.env.local`):
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 3. Start the application
```bash
docker-compose up --build
```

### 4. Access the application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## Project Structure

```
meta-ads-analysis/
├── backend/
│   ├── app/
│   │   ├── api/v1/          # API endpoints
│   │   ├── core/            # Database, Claude client
│   │   ├── models/          # SQLAlchemy models
│   │   ├── schemas/         # Pydantic schemas
│   │   ├── services/        # Business logic
│   │   └── workers/         # Celery tasks
│   ├── alembic/             # Database migrations
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── app/             # Next.js pages
│   │   ├── components/      # React components
│   │   ├── hooks/           # Custom hooks
│   │   ├── lib/             # API client
│   │   ├── stores/          # Zustand stores
│   │   └── types/           # TypeScript types
│   └── Dockerfile
├── docs/                    # PDCA documentation
└── docker-compose.yml
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/ads/collect` | Start ad collection job |
| GET | `/api/v1/ads/collect/{job_id}` | Get collection job status |
| GET | `/api/v1/ads` | List ads with filters |
| GET | `/api/v1/ads/{ad_id}` | Get ad detail with analysis |
| POST | `/api/v1/analysis/image/{ad_id}` | Queue image analysis |
| POST | `/api/v1/analysis/copy/{ad_id}` | Queue copy analysis |
| POST | `/api/v1/analysis/batch` | Queue batch analysis |

## Development

### Run backend locally
```bash
cd backend
poetry install
poetry run uvicorn app.main:app --reload
```

### Run frontend locally
```bash
cd frontend
npm install
npm run dev
```

### Run Celery worker
```bash
cd backend
poetry run celery -A app.workers.celery_app worker --loglevel=info -Q celery,collect,analyze
```

## License

MIT

## Author

Built with Claude Code
