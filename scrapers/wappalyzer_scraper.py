import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import time
from loguru import logger
from Wappalyzer import Wappalyzer, WebPage
from utils.database import init_db, insert_company, insert_technology, get_all_companies

# ─────────────────────────────────────────
# Liste d'entreprises cibles
# ─────────────────────────────────────────
TARGET_COMPANIES = [
    {"name": "Shopify",     "domain": "https://www.shopify.com"},
    {"name": "Stripe",      "domain": "https://www.stripe.com"},
    {"name": "Vercel",      "domain": "https://www.vercel.com"},
    {"name": "Supabase",    "domain": "https://www.supabase.com"},
    {"name": "PlanetScale", "domain": "https://www.planetscale.com"},
]

# ─────────────────────────────────────────
# Fonctions
# ─────────────────────────────────────────
def detect_technologies(url):
    """Détecte les technologies d'un site via Wappalyzer."""
    try:
        logger.info(f"🌐 Analyse Wappalyzer : {url}")
        wappalyzer = Wappalyzer.latest()
        webpage    = WebPage.new_from_url(url, timeout=10)
        techs      = wappalyzer.analyze_with_categories(webpage)
        return techs  # dict : {"React": {"categories": ["JavaScript frameworks"]}, ...}
    except Exception as e:
        logger.error(f"❌ Erreur Wappalyzer pour {url} : {e}")
        return {}


def scrape_company_web(company):
    """Scrape le site web d'une entreprise et sauvegarde en base."""
    name = company["name"]
    url  = company["domain"]

    print(f"\n{'='*50}")
    print(f"🌐 Wappalyzer : {name}")
    print(f"{'='*50}")

    # Récupère l'id de l'entreprise (déjà insérée par github_scraper)
    company_id = insert_company(name, domain=url)

    # Détecte les technologies
    techs = detect_technologies(url)

    if techs:
        print(f"🔍 {len(techs)} technologies détectées :")
        for tech_name, data in techs.items():
            categories = data.get("categories", ["Unknown"])
            category   = categories[0] if categories else "Unknown"
            print(f"   → {tech_name} ({category})")
            insert_technology(company_id, tech_name, source="wappalyzer", category=category)
    else:
        print(f"   ⚠️  Aucune technologie détectée")

    time.sleep(2)  # Pause entre chaque site
    return company_id


# ─────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────
if __name__ == "__main__":
    init_db()
    print("🚀 Démarrage du scraper Wappalyzer...\n")

    for company in TARGET_COMPANIES:
        scrape_company_web(company)

    print(f"\n{'='*50}")
    print("✅ Scraping Wappalyzer terminé !")
    print(f"{'='*50}")
