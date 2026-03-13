# ───────────────────────────────────────── 
# CONFIGURATION DE L'AGENT 
# ───────────────────────────────────────── 
# Adresse et port du serveur 
SERVER_HOST = "127.0.0.1"   # localhost (on testera tout sur le même PC) 
SERVER_PORT = 9000 
# Intervalle d'envoi des métriques (en secondes) 
SEND_INTERVAL = 30 
# Identifiant unique de ce nœud (à changer pour chaque machine) 
import socket 
NODE_ID = socket.gethostname()  # utilise le nom de la machine automatiquement 
# Seuil d'alerte (en pourcentage) 
ALERT_THRESHOLD = 90 
# Services réseau à surveiller (nom affiché, nom du processus système) 
NETWORK_SERVICES = { 
"http"  : 80, 
"https" : 443, 
"ftp"   : 21, 
} 
# Applications à surveiller (nom affiché, nom du processus) 
APP_SERVICES = { 
"firefox" : "firefox.exe", 
"chrome"  : "chrome.exe", 
"vlc"     
: "vlc.exe", 
} 
# Ports à surveiller 
MONITORED_PORTS = [80, 22, 443, 21]