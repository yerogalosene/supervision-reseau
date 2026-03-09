import sqlite3
import queue
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "db", "supervision.db")

class DatabasePool:
    """Pool de connexions SQLite."""

    def __init__(self, pool_size=10):
        self.pool_size = pool_size
        self.pool = queue.Queue(maxsize=pool_size)
        self._create_connections()
        print(f" Pool de connexions créé ({pool_size} connexions)")

    def _create_connections(self):
        """Crée toutes les connexions au démarrage."""
        for _ in range(self.pool_size):
            conn = sqlite3.connect(DB_PATH, check_same_thread=False)
            conn.row_factory = sqlite3.Row  # pour accéder aux colonnes par nom
            self.pool.put(conn)

    def get_connection(self):
        """Récupère une connexion disponible (attend si toutes occupées)."""
        return self.pool.get()

    def release_connection(self, conn):
        """Remet la connexion dans le pool après utilisation."""
        self.pool.put(conn)

    def close_all(self):
        """Ferme toutes les connexions proprement."""
        while not self.pool.empty():
            conn = self.pool.get()
            conn.close()
        print("Pool de connexions fermé.")