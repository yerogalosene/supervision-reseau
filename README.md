# Système Distribué de Supervision Réseau
Projet Systèmes Répartis — M1 SRIV — UN-CHK 2026
Réalisé avec Python 3.12, SQLite, Flask


## Membres du groupe
- Yero Gallo SENE (Chef de projet / Serveur TCP)
- Saikou Oumar THIOUNE (Agent de supervision)
- Khadim DIOP (Interface web)

## Lien du dépôt
https://github.com/yerogalosene/supervision-reseau


## 📋 Description
Système distribué de supervision réseau basé sur une architecture
client-serveur. Des agents collectent les métriques système
(CPU, RAM, Disque, services, ports) et les envoient à un serveur
central qui les stocke et les affiche sur une interface web.

---

## 🏗️ Architecture
```
supervision/
├── agent/
│   ├── agent.py         # Programme principal de l'agent
│   ├── metrics.py       # Collecte des métriques (psutil)
│   └── config.py        # Configuration de l'agent
├── server/
│   ├── server.py        # Serveur TCP multi-clients
│   ├── client_handler.py# Gestionnaire de clients (threads)
│   ├── db_pool.py       # Pool de connexions SQLite
│   ├── database.py      # Requêtes SQL
│   └── watchdog.py      # Détection des nœuds en panne
├── common/
│   └── protocol.py      # Protocole de communication JSON
├── web/
│   ├── app.py           # Interface web Flask
│   ├── templates/
│   │   └── index.html   # Tableau de bord
│   └── static/
│       └── style.css    # Styles (dark mode)
├── db/
│   ├── init_db.sql      # Script création base de données
│   └── init_db.py       # Initialisation de la BD
├── test_charge.py       # Script de tests de charge
└── README.md
```

---

## ⚙️ Installation

### 1. Prérequis
- Python 3.10 ou supérieur
- Git

### 2. Cloner le projet
```bash
git clone <lien_du_repo>
cd supervision
```

### 3. Créer l'environnement virtuel
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux / macOS
source venv/bin/activate
```

### 4. Installer les dépendances
```bash
pip install psutil flask rich
```

### 5. Initialiser la base de données
```bash
python db/init_db.py
```

---

## 🚀 Lancement du système

Ouvrir **3 terminaux** dans le dossier `supervision/` avec le venv activé.

### Terminal 1 — Serveur TCP
```bash
python -m server.server
```

### Terminal 2 — Agent de supervision
```bash
python -m agent.agent
```

### Terminal 3 — Interface web
```bash
python -m web.app
```

Puis ouvrir le navigateur sur :
```
http://127.0.0.1:5000
```

---

## 🧪 Tests de charge

Avec le serveur lancé, exécuter dans un terminal :
```bash
python test_charge.py
```
Ce script simule automatiquement 10, 50 puis 100 agents simultanés
et affiche un tableau récapitulatif des performances.

---

## 📡 Protocole de communication

Format JSON sur socket TCP — 3 types de messages :

**METRICS** (Agent → Serveur) :
```json
{
  "type"     : "METRICS",
  "node_id"  : "PC-YORO",
  "os"       : "Windows 11",
  "cpu_type" : "Intel Core i5",
  "cpu_load" : 45.2,
  "mem_load" : 81.3,
  "disk_load": 60.0,
  "uptime"   : 123456,
  "services" : {"http": "OK", "ssh": "FAIL"},
  "ports"    : {"80": "OPEN", "443": "CLOSED"},
  "alerts"   : []
}
```

**ACK** (Serveur → Agent) :
```json
{"type": "ACK", "status": "OK", "message": "Metrics received"}
```

**COMMAND** (Serveur → Agent) :
```json
{"type": "COMMAND", "action": "UP", "target": "http"}
```

---

## 🗄️ Base de données

SQLite avec 5 tables :
- `nodes` — liste des nœuds supervisés
- `metrics` — métriques reçues (CPU, RAM, Disque, Uptime)
- `services` — statut des services et applications
- `alerts` — alertes générées (dépassement de seuil)
- `logs` — journalisation des événements

Pool de connexions : 10 connexions simultanées (queue.Queue)

---

## 🔧 Configuration

Modifier `agent/config.py` pour changer :
- `SERVER_HOST` — adresse IP du serveur
- `SERVER_PORT` — port TCP (défaut : 9000)
- `SEND_INTERVAL` — intervalle d'envoi en secondes (défaut : 30)
- `ALERT_THRESHOLD` — seuil d'alerte en % (défaut : 90)

---

## 📊 Résultats des tests de charge

| Agents | Succès | Erreurs | Taux   | Temps moyen |
|--------|--------|---------|--------|-------------|
| 10     |30      | 0       |100%    |100.4ms      |
| 50     |150     | 0       |100%    |562.6ms      |
| 100    |285     | 6       |97.9%   |1187.9ms     |



---
