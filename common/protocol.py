import json

# ─────────────────────────────────────────
# CONSTANTES DU PROTOCOLE
# ─────────────────────────────────────────

MSG_METRICS = "METRICS"   # Agent → Serveur
MSG_ACK     = "ACK"       # Serveur → Agent
MSG_COMMAND = "COMMAND"   # Serveur → Agent

ENCODING    = "utf-8"
SEPARATOR   = "\n"        # Séparateur de messages sur le socket

# ─────────────────────────────────────────
# CONSTRUCTION DES MESSAGES
# ─────────────────────────────────────────

def build_metrics_message(node_id, os_name, cpu_type, cpu_load,
                           mem_load, disk_load, uptime,
                           services, ports, alerts):
    """Construit un message de métriques (Agent → Serveur)."""
    message = {
        "type"      : MSG_METRICS,
        "node_id"   : node_id,
        "os"        : os_name,
        "cpu_type"  : cpu_type,
        "cpu_load"  : cpu_load,
        "mem_load"  : mem_load,
        "disk_load" : disk_load,
        "uptime"    : uptime,
        "services"  : services,
        "ports"     : ports,
        "alerts"    : alerts
    }
    return message


def build_ack_message(status="OK", message="Metrics received"):
    """Construit un message d'acquittement (Serveur → Agent)."""
    return {
        "type"    : MSG_ACK,
        "status"  : status,
        "message" : message
    }


def build_command_message(action, target):
    """Construit un message de commande (Serveur → Agent)."""
    return {
        "type"   : MSG_COMMAND,
        "action" : action,
        "target" : target
    }


# ─────────────────────────────────────────
# ENCODAGE / DÉCODAGE
# ─────────────────────────────────────────

def encode(message: dict) -> bytes:
    """Convertit un dictionnaire en bytes pour l'envoi sur le socket."""
    text = json.dumps(message) + SEPARATOR
    return text.encode(ENCODING)


def decode(data: bytes) -> dict:
    """Convertit les bytes reçus du socket en dictionnaire."""
    text = data.decode(ENCODING).strip()
    return json.loads(text)


# ─────────────────────────────────────────
# VALIDATION D'UN MESSAGE
# ─────────────────────────────────────────

REQUIRED_FIELDS = {
    MSG_METRICS : ["type", "node_id", "cpu_load", "mem_load",
                   "disk_load", "uptime", "services", "ports"],
    MSG_ACK     : ["type", "status"],
    MSG_COMMAND : ["type", "action", "target"]
}

def validate(message: dict) -> bool:
    """Vérifie qu'un message contient tous les champs obligatoires."""
    msg_type = message.get("type")
    if msg_type not in REQUIRED_FIELDS:
        return False
    for field in REQUIRED_FIELDS[msg_type]:
        if field not in message:
            return False
    return True