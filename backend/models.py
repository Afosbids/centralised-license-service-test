from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from .database import Base
import datetime

class Brand(Base):
    __tablename__ = "brands"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True) # Contact email for the brand

    products = relationship("Product", back_populates="brand")


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    brand_id = Column(Integer, ForeignKey("brands.id"))

    brand = relationship("Brand", back_populates="products")
    licenses = relationship("License", back_populates="product")


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    
    licenses = relationship("License", back_populates="customer")


class License(Base):
    __tablename__ = "licenses"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    
    is_active = Column(Boolean, default=True)
    expiration_date = Column(DateTime)
    max_seats = Column(Integer, default=1)
    active_seats = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    customer = relationship("Customer", back_populates="licenses")
    product = relationship("Product", back_populates="licenses")
    activations = relationship("Activation", back_populates="license")


class Activation(Base):
    __tablename__ = "activations"

    id = Column(Integer, primary_key=True, index=True)
    license_id = Column(Integer, ForeignKey("licenses.id"))
    machine_id = Column(String, index=True) # Unique ID of the machine/instance
    friendly_name = Column(String, nullable=True) # e.g. "John's MacBook"
    activated_at = Column(DateTime, default=datetime.datetime.utcnow)

    license = relationship("License", back_populates="activations")


class APIKey(Base):
    __tablename__ = "api_keys"

    id = Column(Integer, primary_key=True, index=True)
    key_hash = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)  # Descriptive name for the key
    brand_id = Column(Integer, ForeignKey("brands.id"), nullable=True)  # Optional: associate with brand
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    last_used_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)  # Optional expiration
    
    brand = relationship("Brand", backref="api_keys")
