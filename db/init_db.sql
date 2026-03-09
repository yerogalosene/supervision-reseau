-- Table des noeuds supervisés
CREATE TABLE IF NOT EXISTS nodes (
    node_id     TEXT PRIMARY KEY,
    os          TEXT,
    cpu_type    TEXT,
    last_seen   TEXT,
    status      TEXT DEFAULT 'UP'
);

-- Table des métriques
CREATE TABLE IF NOT EXISTS metrics (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    node_id     TEXT NOT NULL,
    timestamp   TEXT NOT NULL,
    cpu_load    REAL,
    mem_load    REAL,
    disk_load   REAL,
    uptime      INTEGER,
    FOREIGN KEY (node_id) REFERENCES nodes(node_id)
);

-- Table des services et ports
CREATE TABLE IF NOT EXISTS services (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    metric_id   INTEGER NOT NULL,
    name        TEXT NOT NULL,
    status      TEXT NOT NULL,
    FOREIGN KEY (metric_id) REFERENCES metrics(id)
);

-- Table des alertes
CREATE TABLE IF NOT EXISTS alerts (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    node_id     TEXT NOT NULL,
    timestamp   TEXT NOT NULL,
    message     TEXT NOT NULL
);

-- Table des logs
CREATE TABLE IF NOT EXISTS logs (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp   TEXT NOT NULL,
    level       TEXT NOT NULL,
    message     TEXT NOT NULL
);