# scrapers/github_scraper.py
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import requests
import time
from dotenv import load_dotenv
from loguru import logger
from utils.database import init_db, insert_company, insert_technology, get_company_stack

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

# ─────────────────────────────────────────
# Liste d'entreprises cibles
# ─────────────────────────────────────────
TARGET_COMPANIES = [
    {"name": "Shopify",     "github_org": "Shopify",     "domain": "shopify.com"},
    {"name": "Stripe",      "github_org": "stripe",      "domain": "stripe.com"},
    {"name": "Vercel",      "github_org": "vercel",      "domain": "vercel.com"},
    {"name": "Supabase",    "github_org": "supabase",    "domain": "supabase.com"},
    {"name": "PlanetScale", "github_org": "planetscale", "domain": "planetscale.com"},
]

# ─────────────────────────────────────────
# Fonctions de scraping
# ─────────────────────────────────────────
def get_org_languages(org_name, max_repos=10):
    """Récupère tous les langages utilisés par une org GitHub."""
    logger.info(f"🔍 Scraping GitHub : {org_name}")
    lang_count = {}

    url = f"https://api.github.com/orgs/{org_name}/repos?per_page={max_repos}&sort=stars&type=public"
    r = requests.get(url, headers=HEADERS)

    if r.status_code != 200:
        logger.error(f"❌ Erreur GitHub pour {org_name} : {r.status_code}")
        return {}

    repos = r.json()
    logger.info(f"   → {len(repos)} repos trouvés")

    for repo in repos:
        if repo.get("fork"):
            continue  # Ignore les forks

        lang_url = repo["languages_url"]
        lr = requests.get(lang_url, headers=HEADERS)

        if lr.status_code == 200:
            for lang, bytes_count in lr.json().items():
                lang_count[lang] = lang_count.get(lang, 0) + bytes_count

        time.sleep(0.3)  # Respecte la limite GitHub

    return lang_count


def get_org_topics(org_name, max_repos=10):
    """Récupère les topics (tags) des repos d'une org."""
    topics_set = set()

    topics_headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.mercy-preview+json"
    }

    url = f"https://api.github.com/orgs/{org_name}/repos?per_page={max_repos}&sort=stars&type=public"
    r = requests.get(url, headers=topics_headers)

    if r.status_code != 200:
        return topics_set

    for repo in r.json():
        for topic in repo.get("topics", []):
            topics_set.add(topic)

    return topics_set


def scrape_company(company):
    """Scrape une entreprise complète et sauvegarde en base."""
    name   = company["name"]
    org    = company["github_org"]
    domain = company["domain"]

    print(f"\n{'='*50}")
    print(f"🏢 Scraping : {name}")
    print(f"{'='*50}")

    # 1. Insérer l'entreprise — on utilise le NOM comme identifiant
    insert_company(name, domain=domain, github_org=org)

    # 2. Récupérer les langages
    languages = get_org_languages(org)

    if languages:
        sorted_langs = sorted(languages.items(), key=lambda x: x[1], reverse=True)
        print(f"💻 Langages détectés :")
        for lang, bytes_count in sorted_langs[:8]:
            print(f"   → {lang} ({bytes_count:,} bytes)")
            # On passe le NOM de l'entreprise, pas un ID
            insert_technology(name, lang, source="github", category="Language")
    else:
        print(f"   ⚠️  Aucun langage trouvé")

    # 3. Récupérer les topics
    topics = get_org_topics(org)
    if topics:
        print(f"🏷️  Topics : {', '.join(list(topics)[:10])}")
        for topic in topics:
            insert_technology(name, topic, source="github_topics", category="Topic")

    # Retourne le nom (cohérent avec le reste du projet)
    return name


# ─────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────
if __name__ == "__main__":
    init_db()
    print("🚀 Démarrage du scraper GitHub...\n")

    for company in TARGET_COMPANIES:
        scrape_company(company)
        time.sleep(1)  # Pause entre chaque entreprise

    print(f"\n{'='*50}")
    print("✅ Scraping terminé !")
    print(f"{'='*50}")

    # Affiche un résumé
    print("\n📊 RÉSUMÉ — Stack par entreprise :")
    for company in TARGET_COMPANIES:
        stack = get_company_stack(company["name"])
        langs = [r[0] for r in stack if r[1] == "github"]
        print(f"\n🏢 {company['name']} : {', '.join(langs[:5])}")