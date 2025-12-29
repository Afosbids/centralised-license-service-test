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

## Tech Stack

- **Backend**: Python, FastAPI, SQLAlchemy, PostgreSQL
- **Frontend**: React, Vite
- **Database**: PostgreSQL 15 (SQLite supported for development)
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

## Testing

Run the verification script:
```bash
bash verify_backend.sh
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | Database connection string | `sqlite:///./license_system.db` |
| `PYTHONUNBUFFERED` | Python output buffering | `1` |

## Migration from SQLite to PostgreSQL

If you have existing data in SQLite and want to migrate to PostgreSQL:

1. Export data from SQLite (use a migration tool or manual export)
2. Update `DATABASE_URL` to PostgreSQL connection string
3. Restart the backend - tables will be created automatically
4. Import your data into PostgreSQL

## License

MIT
