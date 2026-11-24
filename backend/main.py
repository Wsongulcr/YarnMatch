from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
import models
from database import engine, get_db

# Vérifie et crée les tables dans MySQL au démarrage si elles n'existent pas encore
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="YarnMatch API",
    description="API Back-end de gestion d'inventaire de laine et matching Ravelry",
    version="1.0.0"
)

@app.get("/", tags=["Statut"])
def read_root():
    return {"message": "Serveur YarnMatch opérationnel", "bdd": "Connectée à MySQL"}

@app.get("/yarns/", tags=["Inventaire"])
def get_all_yarns(db: Session = Depends(get_db)):
    # Interroge la table yarn_stash via SQLAlchemy et renvoie toutes les pelotes
    return db.query(models.YarnStash).all()