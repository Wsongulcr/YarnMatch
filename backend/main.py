import math
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

# Densité apparente estimée (en g/cm³) selon la matière du fil
MATERIAL_DENSITY = {
    "coton": 0.38,
    "laine": 0.25,
    "mérinos": 0.26,
    "acrylique": 0.22,
    "alpaga": 0.24,
    "lin": 0.40,
}


def calculate_remaining_meters(
    grams: int,
    diameter_mm: float,
    material: str,
    meters_per_50g: int | None = None
) -> int:
    # 1. Si l'utilisateur connaît le métrage de l'étiquette, calcul exact
    if meters_per_50g:
        return round((grams * meters_per_50g) / 50)

    # 2. Sinon, estimation physique par le diamètre (mm) et la matière
    mat_lower = material.lower()
    density = next((val for key, val in MATERIAL_DENSITY.items() if key in mat_lower), 0.28)
    meters = (4 * grams) / (math.pi * density * (diameter_mm ** 2))
    return max(1, round(meters))


@app.get("/", tags=["Statut"])
def read_root():
    return {"message": "Serveur YarnMatch opérationnel", "bdd": "Connectée à MySQL"}


# --- ROUTES AUTHENTIFICATION ---

@app.post("/auth/register", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED, tags=["Authentification"])
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
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


# --- ROUTES CRUD INVENTAIRE (PROTÉGÉES PAR JWT) ---

@app.post("/yarns/", response_model=schemas.YarnResponse, status_code=status.HTTP_201_CREATED, tags=["Inventaire"])
def create_yarn(
    yarn: schemas.YarnCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    if yarn.diameter_mm <= 0 or yarn.remaining_grams <= 0:
        raise HTTPException(status_code=400, detail="Le diamètre et le poids doivent être supérieurs à 0.")

    calculated_meters = calculate_remaining_meters(
        grams=yarn.remaining_grams,
        diameter_mm=yarn.diameter_mm,
        material=yarn.material,
        meters_per_50g=yarn.meters_per_50g
    )

    new_yarn = models.YarnStash(
        user_id=current_user.id,
        brand=yarn.brand,
        name=yarn.name,
        material=yarn.material,
        diameter_mm=yarn.diameter_mm,
        color_hex=yarn.color_hex,
        remaining_grams=yarn.remaining_grams,
        remaining_meters=calculated_meters
    )
    db.add(new_yarn)
    db.commit()
    db.refresh(new_yarn)
    return new_yarn


@app.get("/yarns/", response_model=list[schemas.YarnResponse], tags=["Inventaire"])
def get_my_yarns(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    return db.query(models.YarnStash).filter(models.YarnStash.user_id == current_user.id).all()


@app.put("/yarns/{yarn_id}", response_model=schemas.YarnResponse, tags=["Inventaire"])
def update_yarn(
    yarn_id: int,
    yarn_update: schemas.YarnUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    db_yarn = db.query(models.YarnStash).filter(
        models.YarnStash.id == yarn_id,
        models.YarnStash.user_id == current_user.id
    ).first()
    if not db_yarn:
        raise HTTPException(status_code=404, detail="Pelote introuvable dans votre stock")

    update_data = yarn_update.model_dump(exclude_unset=True)
    meters_per_50g = update_data.pop("meters_per_50g", None)

    for key, value in update_data.items():
        setattr(db_yarn, key, value)

    if any(k in update_data for k in ("remaining_grams", "diameter_mm", "material")) or meters_per_50g:
        db_yarn.remaining_meters = calculate_remaining_meters(
            grams=db_yarn.remaining_grams,
            diameter_mm=db_yarn.diameter_mm,
            material=db_yarn.material,
            meters_per_50g=meters_per_50g
        )

    db.commit()
    db.refresh(db_yarn)
    return db_yarn


@app.delete("/yarns/{yarn_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Inventaire"])
def delete_yarn(
    yarn_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    db_yarn = db.query(models.YarnStash).filter(
        models.YarnStash.id == yarn_id,
        models.YarnStash.user_id == current_user.id
    ).first()
    if not db_yarn:
        raise HTTPException(status_code=404, detail="Pelote introuvable dans votre stock")

    db.delete(db_yarn)
    db.commit()
    return None