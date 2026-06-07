from sqlalchemy import Column, Integer, String, Float, ForeignKey, Enum, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from database import Base

class RoleEnum(str, enum.Enum):
    admin = "admin"
    delivery = "delivery"

class PaymentMethodEnum(str, enum.Enum):
    cash = "cash"
    mtn_momo = "mtn_momo"
    orange_money = "orange_money"

class OrderStatusEnum(str, enum.Enum):
    pending = "pending"
    processing = "processing"
    delivered = "delivered"
    cancelled = "cancelled"

class PaymentStatusEnum(str, enum.Enum):
    pending = "pending"
    confirmed = "confirmed"

class DeliveryStatusEnum(str, enum.Enum):
    assigned = "assigned"
    in_transit = "in_transit"
    delivered = "delivered"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password = Column(String(100), nullable=False)
    role = Column(Enum(RoleEnum), nullable=False)
    name = Column(String(100), nullable=True)
    phone = Column(String(20), nullable=True)
    address = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    deliveries = relationship("Delivery", back_populates="delivery_person")

class Station(Base):
    __tablename__ = "stations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    logo_url = Column(String(500), nullable=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    address = Column(String(255), nullable=True)
    phone = Column(String(20), nullable=True)
    city = Column(String(100), nullable=False, default="Yaounde")

    cylinders = relationship("GasCylinder", back_populates="station", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="station")

class GasCylinder(Base):
    __tablename__ = "gas_cylinders"

    id = Column(Integer, primary_key=True, index=True)
    station_id = Column(Integer, ForeignKey("stations.id"), nullable=False)
    size_kg = Column(Float, nullable=False)
    stock_quantity = Column(Integer, nullable=False, default=0)
    price = Column(Float, nullable=False)

    station = relationship("Station", back_populates="cylinders")
    orders = relationship("Order", back_populates="cylinder")

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    station_id = Column(Integer, ForeignKey("stations.id"))
    cylinder_id = Column(Integer, ForeignKey("gas_cylinders.id"))
    quantity = Column(Integer, default=1)
    customer_name = Column(String(100), nullable=False)
    customer_phone = Column(String(20), nullable=False)
    customer_town = Column(String(100), nullable=True)
    customer_quarter = Column(String(100), nullable=True)
    customer_address = Column(String(255), nullable=True)
    payment_method = Column(Enum(PaymentMethodEnum))
    payment_status = Column(Enum(PaymentStatusEnum), default=PaymentStatusEnum.pending)
    status = Column(Enum(OrderStatusEnum), default=OrderStatusEnum.pending)
    validation_code = Column(String(10), nullable=True)
    order_date = Column(DateTime(timezone=True), server_default=func.now())

    station = relationship("Station", back_populates="orders")
    cylinder = relationship("GasCylinder", back_populates="orders")
    delivery = relationship("Delivery", back_populates="order", uselist=False)
    payment = relationship("Payment", back_populates="order", uselist=False)

class Delivery(Base):
    __tablename__ = "deliveries"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), unique=True)
    delivery_person_id = Column(Integer, ForeignKey("users.id"))
    delivery_address = Column(String(255), nullable=True)
    status = Column(Enum(DeliveryStatusEnum), default=DeliveryStatusEnum.assigned)
    assigned_at = Column(DateTime(timezone=True), server_default=func.now())
    delivered_at = Column(DateTime(timezone=True), nullable=True)

    order = relationship("Order", back_populates="delivery")
    delivery_person = relationship("User", back_populates="deliveries")

class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), unique=True)
    method = Column(Enum(PaymentMethodEnum), nullable=False)
    amount = Column(Float, nullable=False)
    status = Column(Enum(PaymentStatusEnum), default=PaymentStatusEnum.pending)

    order = relationship("Order", back_populates="payment")
