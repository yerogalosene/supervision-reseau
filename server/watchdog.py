import threading
import time
from datetime import datetime
from server.database import update_node_status, insert_log, insert_alert
from server.client_handler import last_seen

# Temps max sans données avant de considérer un nœud en panne (secondes)
TIMEOUT = 90

class Watchdog(threading.Thread):
    """
    Thread de surveillance qui vérifie régulièrement
    si les nœuds envoient toujours des données.
    """

    def __init__(self, pool):
        super().__init__(daemon=True)
        self.pool = pool
        self.running = True
        print("[WATCHDOG] Démarré — surveillance des nœuds toutes les 30s")

    def run(self):
        while self.running:
            time.sleep(30)  # Vérification toutes les 30s
            self._check_nodes()

    def _check_nodes(self):
        now = datetime.now()
        for node_id, last_time in list(last_seen.items()):
            delta = (now - last_time).total_seconds()
            if delta > TIMEOUT:
                print(f"[WATCHDOG] ❌ Nœud en panne : {node_id} "
                      f"(silence depuis {int(delta)}s)")
                update_node_status(self.pool, node_id, "DOWN")
                insert_alert(self.pool, node_id,
                             f"Nœud en panne — silence depuis {int(delta)}s")
                insert_log(self.pool, "ALERT",
                           f"Nœud {node_id} considéré en panne")

    def stop(self):
        self.running = False