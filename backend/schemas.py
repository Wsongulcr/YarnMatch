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