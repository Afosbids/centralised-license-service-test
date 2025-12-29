# Explanation

## Problem Summary
The requirement was to build a Centralized License Service to manage software entitlements for multiple brands and products. 
The system needs to allow:
1.  **Brands** to issue licenses to **Customers**.
2.  **End-user products** (applications) to validate and activate these licenses.
3.  **Admins** to view licenses associated with a customer.

The core challenge is to ensure licenses have a lifecycle (active/inactive/expired) and enforce seat limits (activations) per license.

## Architecture & Design
I chose a **Three-Tier Architecture**:
1.  **Presentation Layer**: a React Single Page Application (SPA) allows Brands/Admins to interact with the system conveniently.
2.  **Application Layer**: A Python **FastAPI** service handles the business logic, REST API endpoints, and validation.
3.  **Data Layer**: **SQLite** is used as the relational database engine (via SQLAlchemy ORM) for simplicity and portability.

### Data Model
*   **Brands**: The entities that own products (e.g., "Acme", "JetBrains").
*   **Products**: Software or services owned by a brand (e.g., "PhotoEditor", "IDE").
*   **Customers**: The end-users or organizations purchasing licenses.
*   **Licenses**: The relationship between a Customer and a Product. Stores validity, expiration, and seat configurations.
*   **Activations**: Tracks individual machine/instance usage of a license seat. (Added to satisfy US3).

### Key Decisions
*   **FastAPI**: Selected for its high performance, automatic validation (Pydantic), and auto-generated OpenApi documentation.
*   **Separate Frontend**: Although an API-only solution was strictly "required", providing a Dashboard (US6 visualizer) significantly aids usability and debugging.
*   **Activations Table**: Instead of just an integer counter, I normalized activations into a separate table. This is robust for future requirements (e.g., "Deactivate Machine X" - US5) compared to just `active_seats += 1`.

## Trade-offs & Scaling
*   **SQLite**: Great for development but not concurrent. For production, this would be swapped with PostgreSQL.
*   **Auth**: Currently, the API is open. In a real scenario, we would implement OAuth2 or API Keys for Brand authentication.
*   **Seat Locking**: Using database transactions (row locking) would be necessary for high-concurrency activation requests to prevent race conditions on seat counts.

## Implementation Status
*   ✅ **US1 (Provision License)**: Fully Implemented.
*   ✅ **US3 (Activate License)**: Fully Implemented. The `/licenses/activate` endpoint consumes a seat and records the machine ID.
*   ✅ **US4 (Check Status)**: Fully Implemented via `/licenses/validate`.
*   ✅ **US6 (List by Customer)**: Fully Implemented via `GET /customers/{email}/licenses`.
*   ❌ **US2 (Lifecycle)**: Not implemented (Suspend/Resume/Cancel).
*   ❌ **US5 (Deactivate)**: Not implemented (Explicit deactivation endpoint not created, though data model supports it).

## Setup & Run Instructions

### Backend
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```
API will be at: `http://127.0.0.1:8000`
Docs at: `http://127.0.0.1:8000/docs`

### Frontend (Dashboard)
```bash
cd frontend
npm install
npm run dev
```
Dashboard will be at: `http://localhost:5173`

### Sample Requests

**Create Brand:**
```bash
curl -X POST "http://127.0.0.1:8000/brands/" -H "Content-Type: application/json" -d '{"name": "TestBrand", "email": "brand@test.com"}'
```

**Issue License:**
```bash
curl -X POST "http://127.0.0.1:8000/licenses/" -H "Content-Type: application/json" -d '{"customer_id": 1, "product_id": 1, "key": "KEY-123", "max_seats": 5}'
```

**Activate License (Consume Seat):**
```bash
curl -X POST "http://127.0.0.1:8000/licenses/activate" -H "Content-Type: application/json" -d '{"license_key": "KEY-123", "machine_id": "MACHINE-ABC", "friendly_name": "My Laptop"}'
```
