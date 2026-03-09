import sqlite3
import os

# Chemin vers la base de données
DB_PATH = os.path.join(os.path.dirname(__file__), "supervision.db")
SQL_PATH = os.path.join(os.path.dirname(__file__), "init_db.sql")

def init_database():
    """Crée la base de données et toutes les tables."""
    print("Initialisation de la base de données...")

    # Lire le script SQL
    with open(SQL_PATH, "r") as f:
        sql_script = f.read()

    # Connexion et exécution
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.executescript(sql_script)
    conn.commit()
    conn.close()

    print(f" Base de données créée : {DB_PATH}")

if __name__ == "__main__":
    init_database()