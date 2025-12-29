from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from .database import Base
from .main import app, get_db

# Setup in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite://"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the Centralized License System API"}

def test_create_brand():
    response = client.post(
        "/brands/",
        json={"name": "TestBrand", "email": "test@brand.com"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "TestBrand"
    assert "id" in data

def test_create_product():
    # Setup Brand
    client.post("/brands/", json={"name": "ProdBrand", "email": "prod@brand.com"})
    
    response = client.post(
        "/products/",
        json={"name": "TestProduct", "brand_id": 1},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "TestProduct"
    assert data["brand_id"] == 1

def test_create_customer():
    response = client.post(
        "/customers/",
        json={"email": "customer@example.com"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "customer@example.com"

def test_issue_license():
    # Setup
    client.post("/brands/", json={"name": "LicBrand", "email": "lic@brand.com"})
    client.post("/products/", json={"name": "LicProduct", "brand_id": 1})
    client.post("/customers/", json={"email": "lic@cust.com"})

    response = client.post(
        "/licenses/",
        json={"customer_id": 1, "product_id": 1, "max_seats": 5}
    )
    if response.status_code != 200:
        print(response.json())
    assert response.status_code == 200
    data = response.json()
    assert data["max_seats"] == 5
    assert data["active_seats"] == 0
    assert "key" in data

def test_activate_license():
    # Setup
    client.post("/brands/", json={"name": "ActBrand", "email": "act@brand.com"})
    client.post("/products/", json={"name": "ActProduct", "brand_id": 1})
    client.post("/customers/", json={"email": "act@cust.com"})
    lic_res = client.post(
        "/licenses/",
        json={"customer_id": 1, "product_id": 1, "max_seats": 2}
    )
    key = lic_res.json()["key"]

    # Activate
    response = client.post(
        "/licenses/activate",
        json={"license_key": key, "machine_id": "MACHINE-1", "friendly_name": "Test PC"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["machine_id"] == "MACHINE-1"

    # Validate Seat Count
    val_res = client.post(
        "/licenses/validate",
        json={"key": key, "product_id": 1}
    )
    assert val_res.json()["seats_available"] == 1
    assert val_res.json()["activations_count"] == 1

def test_max_seats_limit():
     # Setup
    client.post("/brands/", json={"name": "SeatBrand", "email": "seat@brand.com"})
    client.post("/products/", json={"name": "SeatProduct", "brand_id": 1})
    client.post("/customers/", json={"email": "seat@cust.com"})
    lic_res = client.post(
        "/licenses/",
        json={"customer_id": 1, "product_id": 1, "max_seats": 1}
    )
    key = lic_res.json()["key"]

    # Activate 1
    client.post(
        "/licenses/activate",
        json={"license_key": key, "machine_id": "MACHINE-1"}
    )
    
    # Activate 2 (Should Fail)
    response = client.post(
        "/licenses/activate",
        json={"license_key": key, "machine_id": "MACHINE-2"}
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Max seats reached"
