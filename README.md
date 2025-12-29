# Centralized License System

A full-stack license management system with FastAPI backend and React frontend.

## Features

- Brand and Product Management
- Customer Registration
- License Provisioning and Validation
- License Activation/Deactivation
- License Lifecycle Management (Suspend/Resume)
- Seat-based License Control

## Tech Stack

- **Backend**: Python, FastAPI, SQLAlchemy, SQLite
- **Frontend**: React, Vite
- **Containerization**: Docker, Docker Compose

## Quick Start with Docker

### Prerequisites
- Docker
- Docker Compose

### Running the Application

1. Clone the repository:
```bash
git clone <repository-url>
cd Licence\ System
```

2. Start the services:
```bash
docker-compose up -d
```

3. Access the application:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

4. Stop the services:
```bash
docker-compose down
```

## Manual Setup (Without Docker)

### Backend Setup

```bash
cd backend
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

## License

MIT
