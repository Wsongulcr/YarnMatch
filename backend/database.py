import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Charge les variables de ton fichier .env (s'il existe)
load_dotenv()

# Connexion MySQL configurée par défaut pour Laragon (utilisateur root, sans mot de passe)
# Remplace "yarnmatch_db" par le nom exact de ta base de données dans Laragon
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "mysql+pymysql://root:@localhost:3306/yarnmatch_db"
)

# Création du moteur de connexion à MySQL
engine = create_engine(DATABASE_URL)

# Fabrique de sessions : chaque requête web ouvrira sa propre session temporaire vers la BDD
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Classe mère dont vont hériter toutes nos tables dans models.py
Base = declarative_base()

# Fonction utilitaire pour ouvrir et fermer proprement la connexion BDD à chaque appel API
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()