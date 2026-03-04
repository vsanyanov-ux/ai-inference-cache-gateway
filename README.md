# AI Inference Cache Gateway 🚀

A high-performance microservice layer designed to optimize AI inference by caching results in Redis and logging request metadata to PostgreSQL.

## 🏗 Architecture
- **FastAPI**: Main API framework.
- **Redis**: Caching layer with TTL (1 hour).
- **PostgreSQL**: Request auditing and latency tracking.
- **Transformers**: Hugging Face integration for sentiment analysis.
- **Terraform**: Infrastructure as Code (IaC) for Docker resources.
- **Docker**: Containerized environment using multi-stage builds.
- **GitHub Actions**: CI/CD for automated testing and image building.

## 🚀 Features
- **Predict Endpoint**: `/predict` accepts text and returns ML predictions.
- **Auto-Caching**: Subsequent identical requests are served directly from Redis.
- **Database Logging**: Tracks input, output, latency, and cache hits.
- **Health Monitoring**: `/health` endpoint for monitoring service status.

## 🛠 Setup & Launch

### Prerequisites
- Docker & Docker Compose
- Terraform (optional, for IaC deployment)
- Python 3.10+

### Option 1: Docker Compose (Quick Start)
```bash
docker-compose up --build
```
The API will be available at `http://localhost:8000`.

### Option 2: Terraform (Infrastructure only)
```bash
terraform init
terraform apply
```

### Option 3: Local Development
1. Create venv: `python -m venv venv`
2. Install dependencies: `pip install -r requirements.txt`
3. Run: `uvicorn main:app --reload`

## 🧪 Testing
Run unit tests with pytest:
```bash
pytest
```

## 📊 Documentation
Interactive API docs are available at `/docs` (Swagger UI) when the server is running.

## 🛠 CI/CD
The project includes GitHub Actions workflows for:
- Automatic testing on every push.
- Automated Docker image building.

## 📈 Monitoring
Request logs can be viewed in PostgreSQL on port `5433` (modified to avoid conflicts with Supabase).
