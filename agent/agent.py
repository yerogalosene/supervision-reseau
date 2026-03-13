import socket
import time
import sys
import os

# Permet d'importer les modules du projet
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from agent.config import SERVER_HOST, SERVER_PORT, SEND_INTERVAL, NODE_ID
from agent.metrics import collect_all
from common.protocol import (build_metrics_message, encode,
                              decode, MSG_ACK, MSG_COMMAND)

# ─────────────────────────────────────────
# GESTION DES COMMANDES REÇUES
# ─────────────────────────────────────────

def handle_command(command: dict):
    """Traite une commande reçue du serveur."""
    action = command.get("action")
    target = command.get("target")
    print(f"[COMMANDE] Action={action} sur {target}")
    # Pour l'instant on affiche juste la commande
    # Dans une version avancée on pourrait démarrer/arrêter un service

# ─────────────────────────────────────────
# BOUCLE PRINCIPALE DE L'AGENT
# ─────────────────────────────────────────

def run():
    print(f"[AGENT] Démarrage de l'agent — nœud : {NODE_ID}")
    print(f"[AGENT] Connexion au serveur {SERVER_HOST}:{SERVER_PORT}...")

    while True:
        try:
            # ── Connexion au serveur ──
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((SERVER_HOST, SERVER_PORT))
            print(f"[AGENT] Connecté au serveur ✅")

            while True:
                # ── Collecter les métriques ──
                data = collect_all()
                print(f"[AGENT] Métriques collectées — CPU={data['cpu_load']}% "
                      f"RAM={data['mem_load']}% Disque={data['disk_load']}%")

                # ── Construire et envoyer le message ──
                msg = build_metrics_message(
                    node_id   = data["node_id"],
                    os_name   = data["os"],
                    cpu_type  = data["cpu_type"],
                    cpu_load  = data["cpu_load"],
                    mem_load  = data["mem_load"],
                    disk_load = data["disk_load"],
                    uptime    = data["uptime"],
                    services  = data["services"],
                    ports     = data["ports"],
                    alerts    = data["alerts"]
                )
                sock.sendall(encode(msg))
                print(f"[AGENT] Métriques envoyées au serveur 📤")

                # ── Afficher les alertes éventuelles ──
                if data["alerts"]:
                    for alert in data["alerts"]:
                        print(f"[ALERTE] ⚠️  {alert}")

                # ── Attendre la réponse du serveur ──
                sock.settimeout(10)
                try:
                    response_data = sock.recv(4096)
                    if response_data:
                        response = decode(response_data)
                        if response.get("type") == MSG_ACK:
                            print(f"[AGENT] ACK reçu : {response.get('message')}")
                        elif response.get("type") == MSG_COMMAND:
                            handle_command(response)
                except socket.timeout:
                    print("[AGENT] Pas de réponse du serveur (timeout)")

                # ── Attendre avant le prochain envoi ──
                print(f"[AGENT] Prochain envoi dans {SEND_INTERVAL}s...\n")
                time.sleep(SEND_INTERVAL)

        except ConnectionRefusedError:
            print(f"[AGENT] ❌ Serveur non disponible. Nouvelle tentative dans 10s...")
            time.sleep(10)

        except Exception as e:
            print(f"[AGENT] ❌ Erreur : {e}. Reconnexion dans 10s...")
            time.sleep(10)

        finally:
            try:
                sock.close()
            except:
                pass

if __name__ == "__main__":
    run()

 
