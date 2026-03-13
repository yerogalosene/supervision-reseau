import sys, os
sys.path.append(".")

import socket
import threading
import time
import random
import json
from datetime import datetime
from common.protocol import build_metrics_message, encode, decode

# ─────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────
SERVER_HOST = "127.0.0.1"
SERVER_PORT = 9000
SEND_COUNT  = 3       # Nombre de messages envoyés par agent
SEND_DELAY  = 1       # Délai entre chaque envoi (secondes)

# ─────────────────────────────────────────
# RÉSULTATS GLOBAUX
# ─────────────────────────────────────────
results = {
    "success"  : 0,
    "errors"   : 0,
    "times"    : [],   # temps de réponse en ms
}
lock = threading.Lock()

# ─────────────────────────────────────────
# AGENT SIMULÉ
# ─────────────────────────────────────────

def simulated_agent(node_id: str):
    """Simule un agent qui envoie des métriques au serveur."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        sock.connect((SERVER_HOST, SERVER_PORT))

        for i in range(SEND_COUNT):
            # Générer des métriques aléatoires
            cpu  = round(random.uniform(10, 95), 1)
            mem  = round(random.uniform(30, 95), 1)
            disk = round(random.uniform(20, 80), 1)

            alerts = []
            if cpu  > 90: alerts.append(f"ALERTE : CPU à {cpu}%")
            if mem  > 90: alerts.append(f"ALERTE : RAM à {mem}%")
            if disk > 90: alerts.append(f"ALERTE : Disque à {disk}%")

            msg = build_metrics_message(
                node_id   = node_id,
                os_name   = "Linux Simulation",
                cpu_type  = "Simulated CPU",
                cpu_load  = cpu,
                mem_load  = mem,
                disk_load = disk,
                uptime    = random.randint(100, 99999),
                services  = {
                    "http"   : random.choice(["OK", "FAIL"]),
                    "ssh"    : "OK",
                    "ftp"    : random.choice(["OK", "FAIL"]),
                    "firefox": random.choice(["OK", "FAIL"]),
                    "chrome" : random.choice(["OK", "FAIL"]),
                    "vlc"    : random.choice(["OK", "FAIL"]),
                },
                ports  = {
                    "80" : random.choice(["OPEN", "CLOSED"]),
                    "22" : "OPEN",
                    "443": random.choice(["OPEN", "CLOSED"]),
                    "21" : "CLOSED",
                },
                alerts = alerts
            )

            # Mesurer le temps de réponse
            start = time.time()
            sock.sendall(encode(msg))

            # Attendre l'ACK
            data = sock.recv(4096)
            elapsed = (time.time() - start) * 1000  # en ms

            with lock:
                if data:
                    results["success"] += 1
                    results["times"].append(elapsed)
                else:
                    results["errors"] += 1

            time.sleep(SEND_DELAY)

        sock.close()

    except Exception as e:
        with lock:
            results["errors"] += 1

# ─────────────────────────────────────────
# LANCEMENT DU TEST
# ─────────────────────────────────────────

def run_test(nb_agents: int):
    """Lance nb_agents agents simultanément et mesure les performances."""
    global results
    results = {"success": 0, "errors": 0, "times": []}

    print(f"\n{'='*55}")
    print(f"  🧪 TEST DE CHARGE — {nb_agents} agents simultanés")
    print(f"{'='*55}")
    print(f"  Chaque agent envoie {SEND_COUNT} messages")
    print(f"  Total messages attendus : {nb_agents * SEND_COUNT}")
    print(f"{'='*55}\n")

    threads = []
    start_total = time.time()

    # Créer et lancer tous les threads
    for i in range(nb_agents):
        node_id = f"node-{i+1:03d}"
        t = threading.Thread(target=simulated_agent, args=(node_id,))
        threads.append(t)

    # Démarrer tous les threads en même temps
    for t in threads:
        t.start()

    # Attendre que tous les threads terminent
    for t in threads:
        t.join()

    total_time = time.time() - start_total

    # ── Afficher les résultats ──
    total_msg  = results["success"] + results["errors"]
    success_rate = (results["success"] / total_msg * 100) if total_msg > 0 else 0
    avg_time   = sum(results["times"]) / len(results["times"]) if results["times"] else 0
    min_time   = min(results["times"]) if results["times"] else 0
    max_time   = max(results["times"]) if results["times"] else 0

    print(f"\n{'='*55}")
    print(f"  📊 RÉSULTATS")
    print(f"{'='*55}")
    print(f"  Agents lancés       : {nb_agents}")
    print(f"  Messages envoyés    : {total_msg}")
    print(f"  ✅ Succès           : {results['success']}")
    print(f"  ❌ Erreurs          : {results['errors']}")
    print(f"  Taux de succès      : {success_rate:.1f}%")
    print(f"  Temps total         : {total_time:.2f}s")
    print(f"  Temps réponse moyen : {avg_time:.1f}ms")
    print(f"  Temps réponse min   : {min_time:.1f}ms")
    print(f"  Temps réponse max   : {max_time:.1f}ms")
    print(f"{'='*55}\n")

    return {
        "agents"      : nb_agents,
        "success"     : results["success"],
        "errors"      : results["errors"],
        "success_rate": round(success_rate, 1),
        "total_time"  : round(total_time, 2),
        "avg_time_ms" : round(avg_time, 1),
        "min_time_ms" : round(min_time, 1),
        "max_time_ms" : round(max_time, 1),
    }


# ─────────────────────────────────────────
# PROGRAMME PRINCIPAL
# ─────────────────────────────────────────

if __name__ == "__main__":
    print("\n🚀 DÉMARRAGE DES TESTS DE CHARGE")
    print("Assurez-vous que le serveur est lancé sur le port 9000\n")

    all_results = []

    # Test avec 10, 50 et 100 agents
    for nb in [10, 50, 100]:
        r = run_test(nb)
        all_results.append(r)
        time.sleep(3)  # Pause entre les tests

    # ── Tableau récapitulatif ──
    print("\n" + "="*55)
    print("  📋 TABLEAU RÉCAPITULATIF")
    print("="*55)
    print(f"  {'Agents':<10} {'Succès':<10} {'Erreurs':<10} {'Taux':<10} {'Moy(ms)':<10}")
    print(f"  {'-'*50}")
    for r in all_results:
        print(f"  {r['agents']:<10} {r['success']:<10} {r['errors']:<10} "
              f"{r['success_rate']:<9}% {r['avg_time_ms']:<10}")
    print("="*55)

    # Sauvegarder les résultats dans un fichier JSON
    with open("resultats_tests.json", "w") as f:
        json.dump(all_results, f, indent=2)
    print("\n✅ Résultats sauvegardés dans resultats_tests.json")