from datetime import datetime

# ─────────────────────────────────────────
# NŒUDS
# ─────────────────────────────────────────

def upsert_node(pool, node_id, os_name, cpu_type):
    """Insère ou met à jour un nœud dans la BD."""
    conn = pool.get_connection()
    try:
        now = datetime.now().isoformat()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO nodes (node_id, os, cpu_type, last_seen, status)
            VALUES (?, ?, ?, ?, 'UP')
            ON CONFLICT(node_id) DO UPDATE SET
                last_seen = excluded.last_seen,
                status    = 'UP'
        """, (node_id, os_name, cpu_type, now))
        conn.commit()
    finally:
        pool.release_connection(conn)


def update_node_status(pool, node_id, status):
    """Met à jour le statut d'un nœud (UP ou DOWN)."""
    conn = pool.get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE nodes SET status = ? WHERE node_id = ?
        """, (status, node_id))
        conn.commit()
    finally:
        pool.release_connection(conn)


def get_all_nodes(pool):
    """Retourne tous les nœuds enregistrés."""
    conn = pool.get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM nodes")
        return [dict(row) for row in cursor.fetchall()]
    finally:
        pool.release_connection(conn)


# ─────────────────────────────────────────
# MÉTRIQUES
# ─────────────────────────────────────────

def insert_metrics(pool, node_id, timestamp, cpu_load,
                   mem_load, disk_load, uptime):
    """Insère les métriques dans la BD et retourne l'ID inséré."""
    conn = pool.get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO metrics
                (node_id, timestamp, cpu_load, mem_load, disk_load, uptime)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (node_id, timestamp, cpu_load, mem_load, disk_load, uptime))
        conn.commit()
        return cursor.lastrowid
    finally:
        pool.release_connection(conn)


def insert_services(pool, metric_id, services: dict):
    """Insère les statuts des services liés à une métrique."""
    conn = pool.get_connection()
    try:
        cursor = conn.cursor()
        for name, status in services.items():
            cursor.execute("""
                INSERT INTO services (metric_id, name, status)
                VALUES (?, ?, ?)
            """, (metric_id, name, status))
        conn.commit()
    finally:
        pool.release_connection(conn)


def get_last_metrics(pool, node_id, limit=10):
    """Retourne les dernières métriques d'un nœud."""
    conn = pool.get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM metrics
            WHERE node_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
        """, (node_id, limit))
        return [dict(row) for row in cursor.fetchall()]
    finally:
        pool.release_connection(conn)


# ─────────────────────────────────────────
# ALERTES
# ─────────────────────────────────────────

def insert_alert(pool, node_id, message):
    """Insère une alerte dans la BD."""
    conn = pool.get_connection()
    try:
        now = datetime.now().isoformat()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO alerts (node_id, timestamp, message)
            VALUES (?, ?, ?)
        """, (node_id, now, message))
        conn.commit()
    finally:
        pool.release_connection(conn)


def get_all_alerts(pool, limit=50):
    """Retourne les dernières alertes."""
    conn = pool.get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM alerts
            ORDER BY timestamp DESC
            LIMIT ?
        """, (limit,))
        return [dict(row) for row in cursor.fetchall()]
    finally:
        pool.release_connection(conn)


# ─────────────────────────────────────────
# LOGS
# ─────────────────────────────────────────

def insert_log(pool, level, message):
    """Insère un log dans la BD."""
    conn = pool.get_connection()
    try:
        now = datetime.now().isoformat()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO logs (timestamp, level, message)
            VALUES (?, ?, ?)
        """, (now, level, message))
        conn.commit()
    finally:
        pool.release_connection(conn)