import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import sqlite3
from flask import Flask, render_template, jsonify
from utils.database import get_all_companies, get_company_stack, DB_PATH
from utils.affiliate_links import get_affiliate

app = Flask(__name__)

# ─────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def get_stats():
    """Statistiques globales pour le dashboard."""
    conn = get_db()
    cursor = conn.cursor()
    stats = {}

    cursor.execute("SELECT COUNT(*) FROM companies")
    stats["total_companies"] = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(DISTINCT tech_name) FROM technologies")
    stats["total_techs"] = cursor.fetchone()[0]

    cursor.execute("""
        SELECT tech_name, COUNT(*) as count
        FROM technologies
        GROUP BY tech_name
        ORDER BY count DESC
        LIMIT 10
    """)
    stats["top_techs"] = [{"name": r[0], "count": r[1]} for r in cursor.fetchall()]

    cursor.execute("""
        SELECT source, COUNT(*) as count
        FROM technologies
        GROUP BY source
    """)
    stats["by_source"] = [{"source": r[0], "count": r[1]} for r in cursor.fetchall()]

    cursor.execute("""
        SELECT category, COUNT(*) as count
        FROM technologies
        WHERE category IS NOT NULL
        GROUP BY category
        ORDER BY count DESC
        LIMIT 8
    """)
    stats["by_category"] = [{"category": r[0], "count": r[1]} for r in cursor.fetchall()]

    conn.close()
    return stats


# ─────────────────────────────────────────
# Routes
# ─────────────────────────────────────────
@app.route("/")
def index():
    stats     = get_stats()
    companies = get_all_companies()
    return render_template("index.html", stats=stats, companies=companies)


@app.route("/company/<name>")
def company_detail(name):
    raw_stack = get_company_stack(name)

    # Enrichit chaque techno avec son lien affilié
    stack = []
    for t in raw_stack:
        stack.append({
            "name":      t[0],
            "source":    t[1],
            "category":  t[2] or "—",
            "detected":  t[3] or "—",
            "affiliate": get_affiliate(t[0])
        })

    return render_template("company.html", company_name=name, stack=stack)


@app.route("/api/stats")
def api_stats():
    return jsonify(get_stats())


@app.route("/api/companies")
def api_companies():
    companies = get_all_companies()
    return jsonify([dict(zip(
        ["id","name","domain","industry","size","github_org","created_at"], c
    )) for c in companies])


# ─────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────
if __name__ == "__main__":
    print("🚀 Dashboard démarré → http://localhost:5000")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False)

