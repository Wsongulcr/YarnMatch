from typing import Optional
from pydantic import BaseModel, ConfigDict


# Ce que l'utilisateur envoie pour créer son compte
class UserCreate(BaseModel):
    username: str
    email: str
    password: str


# Ce que l'API renvoie (sans jamais exposer le mot de passe)
class UserResponse(BaseModel):
    id: int
    username: str
    email: str

    model_config = ConfigDict(from_attributes=True)


# Format du jeton JWT renvoyé après connexion
class Token(BaseModel):
    access_token: str
    token_type: str


# Ce que l'utilisateur envoie pour ajouter une pelote
class YarnCreate(BaseModel):
    brand: str
    name: str
    material: str
    diameter_mm: float
    color_hex: str
    remaining_grams: int
    meters_per_50g: Optional[int] = None  # Optionnel : utilisé si l'utilisateur a l'étiquette


# Ce que l'utilisateur peut modifier (tous les champs sont optionnels)
class YarnUpdate(BaseModel):
    brand: Optional[str] = None
    name: Optional[str] = None
    material: Optional[str] = None
    diameter_mm: Optional[float] = None
    color_hex: Optional[str] = None
    remaining_grams: Optional[int] = None
    meters_per_50g: Optional[int] = None


# Ce que l'API renvoie pour chaque pelote
class YarnResponse(BaseModel):
    id: int
    user_id: int
    brand: str
    name: str
    material: str
    diameter_mm: float
    color_hex: str
    remaining_grams: int
    remaining_meters: int

    model_config = ConfigDict(from_attributes=True)