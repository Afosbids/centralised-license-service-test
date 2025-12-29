from fastapi import FastAPI, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List
from . import crud, models, schemas, auth
from .database import SessionLocal, engine
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from .logging_config import setup_logging, get_logger
from .middleware import RequestIDMiddleware, LoggingMiddleware
import uuid

# Setup logging
setup_logging()
logger = get_logger(__name__)

models.Base.metadata.create_all(bind=engine)

logger.info("Database tables created/verified")

# Rate limiting configuration
limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="Centralized License System", version="1.0.0")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Add logging middleware
app.add_middleware(RequestIDMiddleware)
app.add_middleware(LoggingMiddleware)

# CORS configuration
origins = [
    "http://localhost:5173",  # React app default port
    "http://127.0.0.1:5173",
    "https://localhost",
    "https://127.0.0.1",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    logger.info("Health check endpoint called")
    return {"message": "Welcome to the Centralized License System API", "docs": "/docs", "status": "healthy"}

# API Key Management Endpoints
@app.post("/api-keys/", response_model=schemas.APIKeyResponse)
@limiter.limit("10/minute")
def create_api_key(request: Request, api_key: schemas.APIKeyCreate, db: Session = Depends(get_db)):
    """Generate a new API key. The plain key is only shown once!"""
    # Generate plain API key
    plain_key = auth.generate_api_key()
    
    # Hash the key for storage
    key_hash = auth.hash_api_key(plain_key)
    
    # Create API key in database
    db_api_key = crud.create_api_key(db=db, key_hash=key_hash, api_key=api_key)
    
    # Return response with plain key (only time it's shown)
    return schemas.APIKeyResponse(
        id=db_api_key.id,
        key=plain_key,
        name=db_api_key.name,
        brand_id=db_api_key.brand_id,
        created_at=db_api_key.created_at,
        expires_at=db_api_key.expires_at
    )

@app.get("/api-keys/", response_model=List[schemas.APIKey])
@limiter.limit("100/minute")
def list_api_keys(request: Request, skip: int = 0, limit: int = 100, db: Session = Depends(get_db), api_key: models.APIKey = Depends(auth.get_api_key)):
    """List all API keys (requires authentication)"""
    return crud.list_api_keys(db, skip=skip, limit=limit)

@app.delete("/api-keys/{api_key_id}")
@limiter.limit("30/minute")
def revoke_api_key(request: Request, api_key_id: int, db: Session = Depends(get_db), api_key: models.APIKey = Depends(auth.get_api_key)):
    """Revoke (deactivate) an API key"""
    db_api_key = crud.revoke_api_key(db, api_key_id=api_key_id)
    if not db_api_key:
        raise HTTPException(status_code=404, detail="API key not found")
    return {"detail": "API key revoked"}

# Brand Endpoints
@app.post("/brands/", response_model=schemas.Brand)
@limiter.limit("30/minute")
def create_brand(request: Request, brand: schemas.BrandCreate, db: Session = Depends(get_db), api_key: models.APIKey = Depends(auth.get_api_key)):
    db_brand = crud.get_brand_by_name(db, name=brand.name)
    if db_brand:
        raise HTTPException(status_code=400, detail="Brand already registered")
    return crud.create_brand(db=db, brand=brand)

@app.get("/brands/", response_model=List[schemas.Brand])
@limiter.limit("100/minute")
def read_brands(request: Request, skip: int = 0, limit: int = 100, db: Session = Depends(get_db), api_key: models.APIKey = Depends(auth.get_api_key)):
    brands = crud.get_brands(db, skip=skip, limit=limit)
    return brands

# Product Endpoints
@app.post("/products/", response_model=schemas.Product)
@limiter.limit("30/minute")
def create_product(request: Request, product: schemas.ProductCreate, db: Session = Depends(get_db), api_key: models.APIKey = Depends(auth.get_api_key)):
    return crud.create_product(db=db, product=product)

@app.get("/products/", response_model=List[schemas.Product])
@limiter.limit("100/minute")
def read_products(request: Request, skip: int = 0, limit: int = 100, db: Session = Depends(get_db), api_key: models.APIKey = Depends(auth.get_api_key)):
    products = crud.get_products(db, skip=skip, limit=limit)
    return products

# Customer Endpoints
@app.post("/customers/", response_model=schemas.Customer)
@limiter.limit("30/minute")
def create_customer(request: Request, customer: schemas.CustomerCreate, db: Session = Depends(get_db), api_key: models.APIKey = Depends(auth.get_api_key)):
    db_customer = crud.get_customer_by_email(db, email=customer.email)
    if db_customer:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_customer(db=db, customer=customer)

@app.get("/customers/", response_model=List[schemas.Customer])
@limiter.limit("100/minute")
def read_customers(request: Request, skip: int = 0, limit: int = 100, db: Session = Depends(get_db), api_key: models.APIKey = Depends(auth.get_api_key)):
    customers = crud.get_customers(db, skip=skip, limit=limit)
    return customers


@app.get("/customers/{email}/licenses", response_model=List[schemas.License])
@limiter.limit("100/minute")
def read_customer_licenses(request: Request, email: str, db: Session = Depends(get_db), api_key: models.APIKey = Depends(auth.get_api_key)):
    db_customer = crud.get_customer_by_email(db, email=email)
    if not db_customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return crud.get_licenses_by_customer(db, customer_id=db_customer.id)


# License Endpoints
@app.post("/licenses/", response_model=schemas.License)
@limiter.limit("30/minute")
def create_license(request: Request, license: schemas.LicenseCreate, db: Session = Depends(get_db), api_key: models.APIKey = Depends(auth.get_api_key)):
    start_key = license.key if license.key else str(uuid.uuid4())
    # Ensure key validation or auto-generation logic is handled if needed
    # For now, we assume key comes from request or needs generating
    if not license.key:
         license.key = str(uuid.uuid4())
    
    db_license = crud.get_license_by_key(db, key=license.key)
    if db_license:
        raise HTTPException(status_code=400, detail="License key already exists")
    return crud.create_license(db=db, license=license)

@app.post("/licenses/validate", response_model=dict)
@limiter.limit("60/minute")
def validate_license(request: Request, validation: schemas.LicenseValidate, db: Session = Depends(get_db), api_key: models.APIKey = Depends(auth.get_api_key)):
    db_license = crud.get_license_by_key(db, key=validation.key)
    if not db_license:
        raise HTTPException(status_code=404, detail="License not found")
    
    if db_license.product_id != validation.product_id:
         raise HTTPException(status_code=400, detail="License invalid for this product")

    if not db_license.is_active:
         return {"valid": False, "reason": "License is inactive"}
    
    # Check expiration if set
    if db_license.expiration_date:
        import datetime
        if db_license.expiration_date < datetime.datetime.utcnow():
             return {"valid": False, "reason": "License expired"}

    return {"valid": True, "seats_available": db_license.max_seats - db_license.active_seats, "activations_count": db_license.active_seats}

@app.put("/licenses/{license_id}/suspend", response_model=schemas.License)
@limiter.limit("30/minute")
def suspend_license(request: Request, license_id: int, db: Session = Depends(get_db), api_key: models.APIKey = Depends(auth.get_api_key)):
    db_license = crud.get_license(db, license_id=license_id)
    if not db_license:
        raise HTTPException(status_code=404, detail="License not found")
    return crud.update_license_status(db=db, license_id=license_id, is_active=False)

@app.put("/licenses/{license_id}/resume", response_model=schemas.License)
@limiter.limit("30/minute")
def resume_license(request: Request, license_id: int, db: Session = Depends(get_db), api_key: models.APIKey = Depends(auth.get_api_key)):
    db_license = crud.get_license(db, license_id=license_id)
    if not db_license:
        raise HTTPException(status_code=404, detail="License not found")
    return crud.update_license_status(db=db, license_id=license_id, is_active=True)


@app.post("/licenses/activate", response_model=schemas.Activation)
@limiter.limit("60/minute")
def activate_license(request: Request, activation: schemas.ActivationCreate, db: Session = Depends(get_db), api_key: models.APIKey = Depends(auth.get_api_key)):
    # 1. Find License
    db_license = crud.get_license_by_key(db, key=activation.license_key)
    if not db_license:
         raise HTTPException(status_code=404, detail="License not found")
    
    # 2. Check Validity
    if not db_license.is_active:
         raise HTTPException(status_code=400, detail="License is inactive")
    
    if db_license.expiration_date:
        import datetime
        if db_license.expiration_date < datetime.datetime.utcnow():
             raise HTTPException(status_code=400, detail="License expired")

    # 3. Check Duplicate Activation (Idempotency)
    existing_activation = crud.get_activation(db, license_id=db_license.id, machine_id=activation.machine_id)
    if existing_activation:
        return existing_activation

    # 4. Check Seats
    if db_license.active_seats >= db_license.max_seats:
         raise HTTPException(status_code=400, detail="Max seats reached")

    # 5. Create Activation
    return crud.create_activation(db=db, license_id=db_license.id, machine_id=activation.machine_id, friendly_name=activation.friendly_name)

@app.delete("/activations/{activation_id}")
@limiter.limit("30/minute")
def delete_activation(request: Request, activation_id: int, db: Session = Depends(get_db), api_key: models.APIKey = Depends(auth.get_api_key)):
    success = crud.delete_activation(db, activation_id=activation_id)
    if not success:
        raise HTTPException(status_code=404, detail="Activation not found")
    return {"detail": "Activation deleted"}


