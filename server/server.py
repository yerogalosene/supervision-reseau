import socket
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from concurrent.futures import ThreadPoolExecutor
from server.db_pool import DatabasePool
from server.client_handler import handle_client
from server.watchdog import Watchdog
from server.database import insert_log

# ─────────────────────────────────────────
# CONFIGURATION DU SERVEUR
# ─────────────────────────────────────────
HOST        = "0.0.0.0"   # Écoute sur toutes les interfaces réseau
PORT        = 9000
MAX_CLIENTS = 50           # Taille du pool de threads

# ─────────────────────────────────────────
# DÉMARRAGE DU SERVEUR
# ─────────────────────────────────────────

def run():
    # Initialiser le pool de connexions BD
    db_pool = DatabasePool(pool_size=10)
    insert_log(db_pool, "INFO", "Serveur démarré")

    # Démarrer le watchdog
    watchdog = Watchdog(db_pool)
    watchdog.start()

    # Créer le socket serveur
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_sock.bind((HOST, PORT))
    server_sock.listen(MAX_CLIENTS)

    print(f"[SERVEUR] 🚀 En écoute sur {HOST}:{PORT}")
    print(f"[SERVEUR] Pool de threads : {MAX_CLIENTS} workers")
    print(f"[SERVEUR] En attente de connexions...\n")

    # Pool de threads pour gérer les clients
    with ThreadPoolExecutor(max_workers=MAX_CLIENTS) as executor:
        try:
            while True:
                conn, addr = server_sock.accept()
                # Chaque client est géré dans un thread du pool
                executor.submit(handle_client, conn, addr, db_pool)

        except KeyboardInterrupt:
            print("\n[SERVEUR] Arrêt demandé...")
            insert_log(db_pool, "INFO", "Serveur arrêté")

        finally:
            server_sock.close()
            watchdog.stop()
            db_pool.close_all()
            print("[SERVEUR] Serveur arrêté proprement ✅")


if __name__ == "__main__":
    run()