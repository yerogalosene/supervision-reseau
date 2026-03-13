import psutil
import socket
import platform
import time
from agent.config import (NODE_ID, ALERT_THRESHOLD, NETWORK_SERVICES,
                           APP_SERVICES, MONITORED_PORTS)

# ─────────────────────────────────────────
# MÉTRIQUES SYSTÈME
# ─────────────────────────────────────────

def get_cpu_load():
    """Retourne la charge CPU en %."""
    return psutil.cpu_percent(interval=1)

def get_mem_load():
    """Retourne la charge mémoire en %."""
    return psutil.virtual_memory().percent

def get_disk_load():
    """Retourne la charge disque en %."""
    return psutil.disk_usage("/").percent

def get_uptime():
    """Retourne l'uptime du système en secondes."""
    return int(time.time() - psutil.boot_time())

def get_os_info():
    """Retourne le nom du système d'exploitation."""
    return platform.system() + " " + platform.release()

def get_cpu_type():
    """Retourne le type de processeur."""
    return platform.processor()

# ─────────────────────────────────────────
# SERVICES RÉSEAU (vérification des ports)
# ─────────────────────────────────────────

def check_port(port: int, host="127.0.0.1", timeout=1) -> str:
    """Vérifie si un port est ouvert. Retourne OPEN ou CLOSED."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return "OPEN" if result == 0 else "CLOSED"
    except Exception:
        return "CLOSED"

def get_network_services() -> dict:
    """Vérifie le statut des services réseau (par port)."""
    statuses = {}
    for name, port in NETWORK_SERVICES.items():
        statuses[name] = check_port(port)
    return statuses

# ─────────────────────────────────────────
# APPLICATIONS (vérification des processus)
# ─────────────────────────────────────────

def get_running_processes() -> list:
    """Retourne la liste des noms de processus actifs."""
    try:
        return [p.name().lower() for p in psutil.process_iter(['name'])]
    except Exception:
        return []

def get_app_services() -> dict:
    """Vérifie si chaque application est active ou non."""
    running = get_running_processes()
    statuses = {}
    for name, process_name in APP_SERVICES.items():
        statuses[name] = "OK" if process_name.lower() in running else "FAIL"
    return statuses

# ─────────────────────────────────────────
# PORTS SURVEILLÉS
# ─────────────────────────────────────────

def get_monitored_ports() -> dict:
    """Vérifie le statut de tous les ports surveillés."""
    return {str(port): check_port(port) for port in MONITORED_PORTS}

# ─────────────────────────────────────────
# ALERTES
# ─────────────────────────────────────────

def get_alerts(cpu, mem, disk) -> list:
    """Génère des alertes si une métrique dépasse le seuil."""
    alerts = []
    if cpu > ALERT_THRESHOLD:
        alerts.append(f"ALERTE : CPU à {cpu}% (seuil={ALERT_THRESHOLD}%)")
    if mem > ALERT_THRESHOLD:
        alerts.append(f"ALERTE : RAM à {mem}% (seuil={ALERT_THRESHOLD}%)")
    if disk > ALERT_THRESHOLD:
        alerts.append(f"ALERTE : Disque à {disk}% (seuil={ALERT_THRESHOLD}%)")
    return alerts

# ─────────────────────────────────────────
# COLLECTE COMPLÈTE
# ─────────────────────────────────────────

def collect_all() -> dict:
    """Collecte toutes les métriques et retourne un dictionnaire complet."""
    cpu   = get_cpu_load()
    mem   = get_mem_load()
    disk  = get_disk_load()

    # Fusion services réseau + applications
    services = {}
    services.update(get_network_services())
    services.update(get_app_services())

    return {
        "node_id"  : NODE_ID,
        "os"       : get_os_info(),
        "cpu_type" : get_cpu_type(),
        "cpu_load" : cpu,
        "mem_load" : mem,
        "disk_load": disk,
        "uptime"   : get_uptime(),
        "services" : services,
        "ports"    : get_monitored_ports(),
        "alerts"   : get_alerts(cpu, mem, disk)
    }
 
