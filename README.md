# Centralized License System

A full-stack license management system with FastAPI backend and React frontend, using PostgreSQL for production-grade data persistence.

## Features

- Brand and Product Management
- Customer Registration
- License Provisioning and Validation
- License Activation/Deactivation
- License Lifecycle Management (Suspend/Resume)
- Seat-based License Control
- PostgreSQL Database with Connection Pooling
- **API Key Authentication** for secure access
- **Rate Limiting** to prevent abuse
- **HTTPS/SSL** support via Nginx reverse proxy

## Tech Stack

- **Backend**: Python, FastAPI, SQLAlchemy, PostgreSQL
- **Frontend**: React, Vite
- **Database**: PostgreSQL 15 (SQLite supported for development)
- **Authentication**: API Key-based authentication
- **Containerization**: Docker, Docker Compose

## Quick Start with Docker

### Prerequisites
- Docker
- Docker Compose

### Running the Application

1. Clone the repository:
```bash
git clone <repository-url>
cd "Licence System"
```

2. Start all services (PostgreSQL, Backend, Frontend):
```bash
docker-compose up -d
```

This will:
- Start PostgreSQL database on port 5432
- Start Backend API on port 8000
- Start Frontend on port 5173
- Automatically create database tables

3. Access the application:
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

4. Stop the services:
```bash
docker-compose down
```

5. Stop and remove all data:
```bash
docker-compose down -v
```

## Authentication

### Overview
All API endpoints (except `/` and `/docs`) require authentication via API keys. API keys are passed in the `X-API-Key` header.

### Generating an API Key

1. **First API Key** (bootstrap):
```bash
curl -X POST http://localhost:8000/api-keys/ \
  -H "Content-Type: application/json" \
  -d '{"name": "My First Key", "brand_id": null}'
```

Response:
```json
{
  "id": 1,
  "key": "lsk_live_a1b2c3d4e5f6...",  // Save this! Only shown once
  "name": "My First Key",
  "brand_id": null,
  "created_at": "2025-12-29T10:00:00",
  "expires_at": null
}
```

⚠️ **Important**: The plain-text API key is only shown once during creation. Store it securely!

### Using an API Key

Include the API key in the `X-API-Key` header:

```bash
curl -H "X-API-Key: lsk_live_a1b2c3d4e5f6..." \
  http://localhost:8000/brands/
```

### Managing API Keys

**List all API keys:**
```bash
curl -H "X-API-Key: YOUR_KEY" http://localhost:8000/api-keys/
```

**Revoke an API key:**
```bash
curl -X DELETE -H "X-API-Key: YOUR_KEY" \
  http://localhost:8000/api-keys/1
```

### Security Best Practices

1. **Never commit API keys** to version control
2. **Rotate keys regularly** - create new keys and revoke old ones
3. **Use different keys** for different environments (dev, staging, prod)
4. **Set expiration dates** for temporary access
5. **Associate keys with brands** for multi-tenant access control

### Testing Authentication

Run the authentication test script:
```bash
bash test_auth.sh
```

## Rate Limiting

### Overview
All API endpoints are rate-limited to prevent abuse and ensure fair usage. Rate limits are enforced per IP address.

### Rate Limits by Endpoint Type

| Endpoint Type | Limit | Examples |
|---------------|-------|----------|
| **API Key Management** | 10 requests/minute | `POST /api-keys/` |
| **Read Operations** | 100 requests/minute | `GET /brands/`, `GET /customers/` |
| **Write Operations** | 30 requests/minute | `POST /brands/`, `PUT /licenses/{id}/suspend` |
| **License Operations** | 60 requests/minute | `POST /licenses/validate`, `POST /licenses/activate` |

### Rate Limit Headers

Every response includes rate limit information in headers:

```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1735473600
```

- `X-RateLimit-Limit`: Maximum requests allowed in the time window
- `X-RateLimit-Remaining`: Number of requests remaining
- `X-RateLimit-Reset`: Unix timestamp when the limit resets

### Rate Limit Exceeded

When you exceed the rate limit, you'll receive a `429 Too Many Requests` response:

```json
{
  "error": "Rate limit exceeded: 100 per 1 minute"
}
```

**Best Practices:**
1. **Monitor headers**: Check `X-RateLimit-Remaining` to avoid hitting limits
2. **Implement backoff**: Wait for `X-RateLimit-Reset` before retrying
3. **Batch requests**: Combine multiple operations when possible
4. **Cache responses**: Store frequently accessed data locally

### Testing Rate Limits

Run the rate limiting test script:
```bash
bash test_rate_limit.sh
```

## Logging and Monitoring

### Structured Logging
The system uses structured JSON logging for all API requests and business operations. This allows for easy integration with log aggregation tools like ELK Stack, Datadog, or CloudWatch.

### Configuration
You can configure logging via environment variables in `backend/.env`:
- `LOG_LEVEL`: DEBUG, INFO, WARNING, ERROR, CRITICAL (Default: INFO)
- `LOG_FORMAT`: json or text (Default: json)

### Request Tracing
Each request is assigned a unique `X-Request-ID`, which is included in both the logs and the response headers. This allows you to trace a specific request spanning across multiple log entries.

### Log Example (JSON)
```json
{"timestamp": "2025-12-29T11:45:12Z", "level": "INFO", "logger": "backend.main", "message": "License validated successfully", "request_id": "a1b2c3d4", "license_key": "lsk_...", "duration_ms": 15.2}
```

## HTTPS and SSL Configuration

### Overview
The system uses Nginx as a reverse proxy to handle SSL/TLS termination. All traffic is encrypted via HTTPS on port 443, and HTTP traffic on port 80 is automatically redirected to HTTPS.

### Local Development (Self-Signed)
For local development, you can generate self-signed certificates:

1. Run the certificate generation script:
```bash
bash generate_certs.sh
```

This creates `server.crt` and `server.key` in the `nginx/certs/` directory.

2. Start the services with Docker:
```bash
docker-compose up -d
```

3. Access the application:
- **Frontend**: https://localhost
- **Backend API**: https://localhost/api/
- **Documentation**: https://localhost/docs

> [!NOTE]
> Since these are self-signed certificates, your browser will show a security warning. You can safely "Proceed to localhost" for development.

### Production SSL (Let's Encrypt)
In production, it is recommended to use certificates from a trusted CA like Let's Encrypt. You can mount your production certificates into the `license_nginx` container:

```yaml
  nginx:
    volumes:
      - /etc/letsencrypt/live/yourdomain.com/fullchain.pem:/etc/nginx/certs/server.crt:ro
      - /etc/letsencrypt/live/yourdomain.com/privkey.pem:/etc/nginx/certs/server.key:ro
```

### Security Headers
The Nginx configuration includes several security best practices:
- **HSTS**: Force browsers to use HTTPS for the next 6 months.
- **Secure Ciphers**: Only modern, secure TLS protocols (1.2+) and ciphers are enabled.
- **Reverse Proxy**: Protects application servers from direct exposure.

### Testing HTTPS

Run the HTTPS verification script:
```bash
bash test_https.sh
```

## Manual Setup (Without Docker)

### Backend Setup

1. Install PostgreSQL (or use SQLite for development)

2. Create a `.env` file in the `backend` directory:
```bash
cd backend
cp .env.example .env
```

3. Edit `.env` with your database configuration:
```env
# For PostgreSQL
DATABASE_URL=postgresql://license_user:license_password@localhost:5432/license_db

# For SQLite (development only)
# DATABASE_URL=sqlite:///./license_system.db
```

4. Install dependencies and run:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

## Database Configuration

### PostgreSQL (Recommended for Production)

The system uses PostgreSQL by default when running with Docker. For manual setup:

1. Create database and user:
```sql
CREATE DATABASE license_db;
CREATE USER license_user WITH PASSWORD 'license_password';
GRANT ALL PRIVILEGES ON DATABASE license_db TO license_user;
```

2. Set `DATABASE_URL` in `backend/.env`:
```env
DATABASE_URL=postgresql://license_user:license_password@localhost:5432/license_db
```

### SQLite (Development Only)

For quick local development without PostgreSQL:

```env
DATABASE_URL=sqlite:///./license_system.db
```

**Note**: SQLite has limited concurrency support and is not recommended for production.

## API Endpoints

### Brands
- `POST /brands/` - Create a brand
- `GET /brands/` - List all brands

### Products
- `POST /products/` - Create a product
- `GET /products/` - List all products

### Customers
- `POST /customers/` - Register a customer
- `GET /customers/` - List all customers
- `GET /customers/{email}/licenses` - Get licenses for a customer

### Licenses
- `POST /licenses/` - Issue a new license
- `POST /licenses/validate` - Validate a license
- `POST /licenses/activate` - Activate a license on a machine
- `PUT /licenses/{id}/suspend` - Suspend a license
- `PUT /licenses/{id}/resume` - Resume a license

### Activations
- `DELETE /activations/{id}` - Deactivate a machine

## Environment Variables

### Backend Configuration (`backend/.env`)

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | Database connection string | `sqlite:///./license_system.db` |
| `LOG_LEVEL` | Logging level (DEBUG, INFO, etc.) | `INFO` |
| `LOG_FORMAT` | Log format (json, text) | `json` |
| `CORS_ORIGINS` | Comma-separated allowed origins | `http://localhost:5173,https://localhost` |
| `API_KEY_PREFIX` | Prefix for generated API keys | `lsk_live_` |
| `RATE_LIMIT_READ` | Read endpoint rate limit | `100` |
| `RATE_LIMIT_WRITE`| Write endpoint rate limit | `30` |
| `APP_NAME` | Application name for API docs | `Centralized License System` |

### Frontend Configuration (`frontend/.env`)

| Variable | Description | Default |
|----------|-------------|---------|
| `VITE_API_BASE_URL`| Base URL for the backend API | `https://localhost/api` |

## Migration from SQLite to PostgreSQL

If you have existing data in SQLite and want to migrate to PostgreSQL:

1. Export data from SQLite (use a migration tool or manual export)
2. Update `DATABASE_URL` to PostgreSQL connection string
3. Restart the backend - tables will be created automatically
4. Import your data into PostgreSQL

## License

MIT
