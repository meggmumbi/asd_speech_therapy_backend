from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from ..schemas.caregiver import CaregiverCreate
from ..models.caregiver import Caregiver
from ..database import get_db
from ..utils.auth import get_password_hash, create_access_token, verify_password

router = APIRouter()


@router.post("/register")
def register(caregiver: CaregiverCreate, db: Session = Depends(get_db)):
    db_caregiver = db.query(Caregiver).filter(Caregiver.email == caregiver.email).first()
    if db_caregiver:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_password = get_password_hash(caregiver.password)
    new_caregiver = Caregiver(
        username=caregiver.username,
        email=caregiver.email,
        hashed_password=hashed_password
    )
    db.add(new_caregiver)
    db.commit()
    db.refresh(new_caregiver)
    return {"message": "Caregiver created successfully"}


@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    caregiver = db.query(Caregiver).filter(Caregiver.username == form_data.username).first()
    if not caregiver or not verify_password(form_data.password, caregiver.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    access_token = create_access_token(data={"sub": caregiver.username})
    return {"access_token": access_token, "token_type": "bearer"}