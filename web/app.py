import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from flask import Flask, render_template, jsonify, request
from server.db_pool import DatabasePool
from server.database import (get_all_nodes, get_last_metrics,
                              get_all_alerts, insert_log)
from common.protocol import build_command_message, encode
from server.client_handler import active_connections

app = Flask(__name__)
db_pool = DatabasePool(pool_size=5)

# ─────────────────────────────────────────
# PAGES
# ─────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")

# ─────────────────────────────────────────
# API JSON
# ─────────────────────────────────────────

@app.route("/api/nodes")
def api_nodes():
    nodes = get_all_nodes(db_pool)
    return jsonify(nodes)

@app.route("/api/metrics/<node_id>")
def api_metrics(node_id):
    metrics = get_last_metrics(db_pool, node_id, limit=20)
    return jsonify(metrics)

@app.route("/api/alerts")
def api_alerts():
    alerts = get_all_alerts(db_pool, limit=30)
    return jsonify(alerts)

@app.route("/api/command", methods=["POST"])
def api_command():
    data    = request.get_json()
    node_id = data.get("node_id")
    action  = data.get("action", "UP")
    target  = data.get("target")

    if node_id not in active_connections:
        return jsonify({"status": "error",
                        "message": f"Nœud {node_id} non connecté"}), 404

    try:
        conn = active_connections[node_id]
        cmd  = build_command_message(action, target)
        conn.sendall(encode(cmd))
        insert_log(db_pool, "INFO",
                   f"Commande {action} envoyée à {node_id} → {target}")
        return jsonify({"status": "ok",
                        "message": f"Commande envoyée à {node_id}"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# ─────────────────────────────────────────
# LANCEMENT
# ─────────────────────────────────────────

if __name__ == "__main__":
    print("[WEB] Interface disponible sur http://127.0.0.1:5000")
    app.run(debug=True, use_reloader=False)
