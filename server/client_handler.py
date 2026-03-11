import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from datetime import datetime
from common.protocol import decode, encode, build_ack_message, validate
from server.database import (upsert_node, insert_metrics,
                              insert_services, insert_alert, insert_log)

# ─────────────────────────────────────────
# DICTIONNAIRES PARTAGÉS
# ─────────────────────────────────────────

# node_id → datetime du dernier message reçu (utilisé par le watchdog)
last_seen = {}

# node_id → socket de connexion active (utilisé par l'interface web)
active_connections = {}


# ─────────────────────────────────────────
# GESTIONNAIRE D'UN CLIENT
# ─────────────────────────────────────────

def handle_client(conn, addr, pool):
    """
    Fonction exécutée dans un thread du pool pour chaque client connecté.
    Reçoit les messages, les valide, les stocke en BD.
    """
    print(f"[SERVEUR] Nouvelle connexion : {addr}")
    insert_log(pool, "INFO", f"Nouvelle connexion depuis {addr}")
    node_id = None

    try:
        buffer = ""
        while True:
            # ── Réception des données ──
            data = conn.recv(4096)
            if not data:
                print(f"[SERVEUR] Client {addr} déconnecté.")
                break

            # ── Accumulation dans le buffer ──
            buffer += data.decode("utf-8")

            # ── Traitement de chaque message complet (séparé par \n) ──
            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)
                line = line.strip()
                if not line:
                    continue

                try:
                    message = decode(line.encode("utf-8"))
                except Exception as e:
                    print(f"[SERVEUR] ❌ Message invalide de {addr} : {e}")
                    continue

                # ── Validation du message ──
                if not validate(message):
                    print(f"[SERVEUR] ❌ Message mal formé de {addr}")
                    ack = build_ack_message("ERROR", "Message mal formé")
                    conn.sendall(encode(ack))
                    continue

                # ── Traitement du message METRICS ──
                node_id   = message["node_id"]
                timestamp = datetime.now().isoformat()

                # Enregistrer la connexion active
                active_connections[node_id] = conn

                # Mettre à jour le timestamp pour le watchdog
                last_seen[node_id] = datetime.now()

                # Sauvegarder le nœud
                upsert_node(pool, node_id,
                            message.get("os", ""),
                            message.get("cpu_type", ""))

                # Sauvegarder les métriques
                metric_id = insert_metrics(
                    pool, node_id, timestamp,
                    message["cpu_load"],
                    message["mem_load"],
                    message["disk_load"],
                    message["uptime"]
                )

                # Sauvegarder les services
                insert_services(pool, metric_id, message.get("services", {}))

                # Sauvegarder les alertes
                for alert in message.get("alerts", []):
                    insert_alert(pool, node_id, alert)
                    insert_log(pool, "ALERT", f"[{node_id}] {alert}")
                    print(f"[ALERTE] ⚠️  {node_id} : {alert}")

                print(f"[SERVEUR] ✅ Métriques reçues de {node_id} — "
                      f"CPU={message['cpu_load']}% "
                      f"RAM={message['mem_load']}% "
                      f"Disque={message['disk_load']}%")

                # ── Envoyer l'ACK au client ──
                ack = build_ack_message("OK", "Metrics received")
                conn.sendall(encode(ack))

    except Exception as e:
        print(f"[SERVEUR] ❌ Erreur avec {addr} : {e}")

    finally:
        conn.close()
        # Nettoyer les dictionnaires
        if node_id:
            active_connections.pop(node_id, None)
            insert_log(pool, "INFO", f"Déconnexion de {node_id}")
        print(f"[SERVEUR] Connexion fermée : {addr}")