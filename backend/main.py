from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import models
import schemas
import auth
from database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="YarnMatch API",
    description="API Back-end de gestion d'inventaire de laine et matching Ravelry",
    version="1.0.0"
)


@app.get("/", tags=["Statut"])
def read_root():
    return {"message": "Serveur YarnMatch opérationnel", "bdd": "Connectée à MySQL"}


@app.post("/auth/register", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED, tags=["Authentification"])
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Vérifie si l'email ou le pseudo existe déjà
    existing = db.query(models.User).filter(
        (models.User.email == user.email) | (models.User.username == user.username)
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Ce nom d'utilisateur ou cet email est déjà utilisé.")

    new_user = models.User(
        username=user.username,
        email=user.email,
        password_hash=auth.hash_password(user.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@app.post("/auth/login", response_model=schemas.Token, tags=["Authentification"])
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Identifiants incorrects",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = auth.create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/auth/me", response_model=schemas.UserResponse, tags=["Authentification"])
def read_current_user(current_user: models.User = Depends(auth.get_current_user)):
    return current_user