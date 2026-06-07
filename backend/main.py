from fastapi import FastAPI, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List

import random
import string
import models, schemas, database

# Create tables
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="Gas Distribution API")

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins for simple HTML deployment
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.on_event("startup")
def startup_event():
    # Seed data if empty
    db = database.SessionLocal()
    if not db.query(models.Station).first():
        print("Seeding database...")
        # Yaounde Stations
        y_stations = [
            {"name": "Emana Gas", "city": "Yaounde", "lat": 3.8480, "lng": 11.5021},
            {"name": "Mvog-Mbi Station", "city": "Yaounde", "lat": 3.8667, "lng": 11.5167},
            {"name": "Nkolmbong Hub", "city": "Yaounde", "lat": 3.8500, "lng": 11.5000},
            {"name": "Etoug-Ebe Point", "city": "Yaounde", "lat": 3.8600, "lng": 11.4800},
            {"name": "Nsimeyong Supply", "city": "Yaounde", "lat": 3.8550, "lng": 11.5100},
            {"name": "Mfandena Reserve", "city": "Yaounde", "lat": 3.8700, "lng": 11.5200},
        ]
        # Douala Stations
        d_stations = [
            {"name": "Akwa Depot", "city": "Douala", "lat": 4.0511, "lng": 9.7085},
            {"name": "Bonanjo Source", "city": "Douala", "lat": 4.0411, "lng": 9.6953},
            {"name": "Deido Point", "city": "Douala", "lat": 4.0600, "lng": 9.7100},
            {"name": "Makepe Gas", "city": "Douala", "lat": 4.0700, "lng": 9.7500},
        ]
        
        for s in y_stations + d_stations:
            station = models.Station(name=s["name"], city=s["city"], latitude=s["lat"], longitude=s["lng"])
            db.add(station)
            db.commit()
            db.refresh(station)
            
            # Add some cylinders
            c1 = models.GasCylinder(station_id=station.id, size_kg=6.0, stock_quantity=10, price=3000)
            c2 = models.GasCylinder(station_id=station.id, size_kg=12.5, stock_quantity=5, price=6500)
            db.add_all([c1, c2])
        
        db.commit()

    if not db.query(models.User).first():
        print("Seeding users...")
        users = [
            models.User(username="admin", password="admin123", role=models.RoleEnum.admin, name="Admin User"),
            models.User(username="delivery1", password="del123", role=models.RoleEnum.delivery, name="John Driver"),
            models.User(username="delivery2", password="del123", role=models.RoleEnum.delivery, name="Jane Driver")
        ]
        db.add_all(users)
        db.commit()

    db.close()


@app.get("/api/stations", response_model=List[schemas.Station])
def read_stations(db: Session = Depends(get_db)):
    return db.query(models.Station).all()

@app.get("/api/stations/{station_id}", response_model=schemas.Station)
def read_station(station_id: int, db: Session = Depends(get_db)):
    station = db.query(models.Station).filter(models.Station.id == station_id).first()
    if station is None:
        raise HTTPException(status_code=404, detail="Station not found")
    return station

@app.post("/api/orders", response_model=schemas.Order)
def create_order(order: schemas.OrderCreate, db: Session = Depends(get_db)):
    # Check cylinder stock
    cylinder = db.query(models.GasCylinder).filter(models.GasCylinder.id == order.cylinder_id).first()
    if not cylinder or cylinder.stock_quantity < order.quantity:
        raise HTTPException(status_code=400, detail="Not enough stock available")
    
    # Decrement stock
    cylinder.stock_quantity -= order.quantity
    
    
    # Generate 4-digit validation code
    val_code = ''.join(random.choices(string.digits, k=4))
    
    db_order = models.Order(**order.dict(), validation_code=val_code)
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order

@app.post("/api/auth/login", response_model=schemas.LoginResponse)
def login(request: schemas.LoginRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == request.username, models.User.password == request.password).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"id": user.id, "username": user.username, "role": user.role}

@app.get("/api/orders", response_model=List[schemas.OrderWithDetails])
def get_all_orders(db: Session = Depends(get_db)):
    return db.query(models.Order).all()

@app.put("/api/orders/{order_id}/assign")
def assign_delivery(order_id: int, delivery_person_id: int, db: Session = Depends(get_db)):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    user = db.query(models.User).filter(models.User.id == delivery_person_id, models.User.role == models.RoleEnum.delivery).first()
    if not user:
        raise HTTPException(status_code=404, detail="Delivery person not found")

    order.status = models.OrderStatusEnum.processing
    
    delivery = models.Delivery(order_id=order.id, delivery_person_id=user.id, status=models.DeliveryStatusEnum.assigned)
    db.add(delivery)
    db.commit()
    return {"message": "Delivery assigned successfully"}

@app.get("/api/deliveries/{user_id}", response_model=List[schemas.OrderWithDetails])
def get_deliveries_for_user(user_id: int, db: Session = Depends(get_db)):
    deliveries = db.query(models.Delivery).filter(models.Delivery.delivery_person_id == user_id).all()
    orders = [d.order for d in deliveries]
    return orders

@app.put("/api/deliveries/{order_id}/complete")
def complete_delivery(order_id: int, validation_code: str, db: Session = Depends(get_db)):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if order.validation_code != validation_code:
        raise HTTPException(status_code=400, detail="Invalid validation code")
    
    order.status = models.OrderStatusEnum.delivered
    order.payment_status = models.PaymentStatusEnum.confirmed
    
    delivery = db.query(models.Delivery).filter(models.Delivery.order_id == order.id).first()
    if delivery:
        delivery.status = models.DeliveryStatusEnum.delivered
        
    db.commit()
    return {"message": "Delivery completed successfully"}
    
@app.get("/api/delivery-staff", response_model=List[schemas.User])
def get_delivery_staff(db: Session = Depends(get_db)):
    return db.query(models.User).filter(models.User.role == models.RoleEnum.delivery).all()

# Mount the frontend static files at the root
import os
frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend")
app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")
