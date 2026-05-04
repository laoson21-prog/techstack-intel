# utils/database.py
import sqlite3
import os

DB_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', 'data', 'techstack.db')
)


# ─────────────────────────────────────────
# CONNEXION UNIQUE AVEC WAL (anti-lock)
# ─────────────────────────────────────────
def get_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH, timeout=30, check_same_thread=False)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    conn.row_factory = sqlite3.Row
    return conn


# ─────────────────────────────────────────
# INITIALISATION
# ─────────────────────────────────────────
def init_db():
    """Crée les tables si elles n'existent pas encore."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS companies (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            name       TEXT    UNIQUE NOT NULL,
            domain     TEXT,
            industry   TEXT,
            size       TEXT,
            github_org TEXT,
            created_at TEXT    DEFAULT (datetime('now'))
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS technologies (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            company_name TEXT NOT NULL,
            tech_name    TEXT NOT NULL,
            source       TEXT NOT NULL,
            category     TEXT,
            detected_at  TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (company_name) REFERENCES companies(name)
        )
    """)

    conn.commit()
    conn.close()


# ─────────────────────────────────────────
# LECTURE
# ─────────────────────────────────────────
def get_all_companies():
    """Retourne toutes les entreprises."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM companies ORDER BY name")
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_company_stack(company_name: str):
    """Retourne la stack dedupliquee d'une entreprise."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT DISTINCT
            tech_name,
            source,
            category,
            MAX(detected_at) as detected_at
        FROM technologies
        WHERE company_name = ?
        GROUP BY tech_name, source, category
        ORDER BY source, tech_name
    """, (company_name,))
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_tech_stats():
    """Statistiques globales pour le dashboard."""
    conn = get_db()
    cursor = conn.cursor()
    stats = {}

    cursor.execute("SELECT COUNT(*) FROM companies")
    stats["total_companies"] = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(DISTINCT tech_name) FROM technologies")
    stats["total_techs"] = cursor.fetchone()[0]

    cursor.execute("""
        SELECT tech_name, COUNT(DISTINCT company_name) as cnt
        FROM technologies
        GROUP BY tech_name
        ORDER BY cnt DESC
        LIMIT 10
    """)
    stats["top_techs"] = [{"name": r[0], "count": r[1]}
                           for r in cursor.fetchall()]

    cursor.execute("""
        SELECT source, COUNT(*) as cnt
        FROM technologies
        GROUP BY source
    """)
    stats["by_source"] = [{"source": r[0], "count": r[1]}
                           for r in cursor.fetchall()]

    cursor.execute("""
        SELECT category, COUNT(*) as cnt
        FROM technologies
        WHERE category IS NOT NULL
        GROUP BY category
        ORDER BY cnt DESC
        LIMIT 8
    """)
    stats["by_category"] = [{"category": r[0], "count": r[1]}
                             for r in cursor.fetchall()]

    conn.close()
    return stats


# ─────────────────────────────────────────
# ECRITURE
# ─────────────────────────────────────────
def save_company(company: dict) -> str:
    """Insere ou ignore une entreprise. Retourne le nom."""
    if not company.get("name"):
        return ""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR IGNORE INTO companies (name, domain, industry, github_org)
        VALUES (:name, :domain, :industry, :github_org)
    """, {
        "name":       company.get("name", ""),
        "domain":     company.get("domain", ""),
        "industry":   company.get("industry", ""),
        "github_org": company.get("github_org", ""),
    })
    conn.commit()
    conn.close()
    return company["name"]


def save_technology(company_name: str, tech_name: str,
                    source: str, category: str = None):
    """Insere une technologie detectee."""
    if not company_name or not tech_name or not source:
        print(f"⚠️  save_technology ignorée — valeur nulle : "
              f"company={company_name} tech={tech_name} source={source}")
        return
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO technologies (company_name, tech_name, source, category)
        VALUES (?, ?, ?, ?)
    """, (company_name, tech_name, source, category))
    conn.commit()
    conn.close()


# ─────────────────────────────────────────
# ALIASES — compatibilite totale avec les scrapers
# Modes supportes :
#   insert_company({"name": "X", "domain": "..."})
#   insert_company("X", domain="...", github_org="...")
#   insert_company(name="X", domain="...")
# ─────────────────────────────────────────
def insert_company(name_or_dict=None, name: str = None, domain: str = "",
                   industry: str = "", size: str = "", github_org: str = "") -> str:
    """
    Alias flexible de save_company. Retourne toujours le nom (str).
    Ne retourne JAMAIS un ID entier — les scrapers utilisent le nom comme clé.
    """
    if isinstance(name_or_dict, dict):
        return save_company(name_or_dict)
    else:
        resolved_name = name_or_dict or name or ""
        return save_company({
            "name":       resolved_name,
            "domain":     domain,
            "industry":   industry,
            "github_org": github_org,
        })


def insert_technology(company_name: str = None, tech_name: str = None,
                      source: str = None, category: str = None,
                      name: str = None, tech: str = None, src: str = None):
    """
    Alias flexible de save_technology.
    Accepte les kwargs alternatifs :
      name= au lieu de company_name=
      tech= au lieu de tech_name=
      src=  au lieu de source=
    """
    resolved_company = company_name or name
    resolved_tech    = tech_name    or tech
    resolved_source  = source       or src
    save_technology(resolved_company, resolved_tech, resolved_source, category)


# ─────────────────────────────────────────
# AUTO-INIT au premier import
# ─────────────────────────────────────────
init_db()