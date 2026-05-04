import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from loguru import logger
from datetime import datetime

from scrapers.github_scraper import scrape_company as scrape_github
from scrapers.wappalyzer_scraper import scrape_company_web
from utils.database import init_db, get_all_companies, get_company_stack
from utils.notifier import send_alert_email, build_alert_html
from utils.report_generator import generate_monthly_report

# ─────────────────────────────────────────
# Entreprises cibles
# ─────────────────────────────────────────
TARGET_COMPANIES = [
    {"name": "Shopify",     "github_org": "Shopify",     "domain": "https://www.shopify.com"},
    {"name": "Stripe",      "github_org": "stripe",      "domain": "https://www.stripe.com"},
    {"name": "Vercel",      "github_org": "vercel",      "domain": "https://www.vercel.com"},
    {"name": "Supabase",    "github_org": "supabase",    "domain": "https://www.supabase.com"},
    {"name": "PlanetScale", "github_org": "planetscale", "domain": "https://www.planetscale.com"},
]

# ─────────────────────────────────────────
# Jobs
# ─────────────────────────────────────────
def run_github_scraper():
    logger.info(f"⏰ [{datetime.now()}] Lancement scraper GitHub...")
    for company in TARGET_COMPANIES:
        try:
            scrape_github(company)
        except Exception as e:
            logger.error(f"❌ GitHub scraper erreur ({company['name']}) : {e}")
    logger.info("✅ Scraper GitHub terminé")


def run_wappalyzer_scraper():
    logger.info(f"⏰ [{datetime.now()}] Lancement scraper Wappalyzer...")
    for company in TARGET_COMPANIES:
        try:
            scrape_company_web(company)
        except Exception as e:
            logger.error(f"❌ Wappalyzer scraper erreur ({company['name']}) : {e}")
    logger.info("✅ Scraper Wappalyzer terminé")


def check_and_notify():
    """Détecte les nouvelles techs du jour et envoie des alertes email."""
    logger.info("📧 Vérification des changements de stack...")
    companies = get_all_companies()
    today     = datetime.now().strftime("%Y-%m-%d")
    alerted   = 0

    for company in companies:
        name  = company[1]
        stack = get_company_stack(name)

        # Filtre uniquement les techs détectées aujourd'hui
        new_techs = [
            {"name": t[0], "source": t[1], "category": t[2]}
            for t in stack
            if t[3] and t[3].startswith(today)
        ]

        if new_techs:
            logger.info(f"🆕 {len(new_techs)} nouvelles techs pour {name} → envoi email")
            html = build_alert_html(name, new_techs)
            send_alert_email(
                subject=f"🔍 TechStack Intel — {name} : {len(new_techs)} nouvelles techs détectées",
                html_body=html
            )
            alerted += 1
        else:
            logger.info(f"   → {name} : aucun changement aujourd'hui")

    if alerted == 0:
        logger.info("✅ Aucune alerte à envoyer aujourd'hui")
    else:
        logger.info(f"✅ {alerted} alerte(s) email envoyée(s)")


def run_monthly_report():
    """Génère le rapport PDF mensuel et envoie par email."""
    logger.info(f"📄 [{datetime.now()}] Génération du rapport PDF mensuel...")
    try:
        pdf_path = generate_monthly_report()
        logger.info(f"✅ Rapport généré : {pdf_path}")

        # Notifie par email que le rapport est prêt
        month = datetime.now().strftime("%B %Y")
        html  = f"""
        <div style="font-family:sans-serif;background:#0f1117;color:#e2e8f0;padding:32px;border-radius:12px;">
          <h2 style="color:#63b3ed;">📊 Rapport mensuel disponible</h2>
          <p style="color:#a0aec0;margin-top:12px;">
            Ton rapport <strong>TechStack Intel — {month}</strong> a été généré automatiquement.
          </p>
          <div style="margin-top:20px;padding:16px;background:#1a1f2e;border-radius:8px;">
            <p style="color:#718096;font-size:0.9rem;">📁 Fichier généré :</p>
            <p style="color:#63b3ed;font-weight:bold;">{pdf_path}</p>
          </div>
          <p style="color:#718096;margin-top:20px;font-size:0.85rem;">
            Tu peux le vendre sur Gumroad ou l'envoyer à tes abonnés.
          </p>
        </div>
        """
        send_alert_email(
            subject=f"📊 TechStack Intel — Rapport {month} généré",
            html_body=html
        )
        logger.info("✅ Notification email du rapport envoyée")

    except Exception as e:
        logger.error(f"❌ Erreur génération rapport PDF : {e}")


def run_all():
    """Lance tous les scrapers puis vérifie les alertes."""
    logger.info("🚀 Lancement de tous les scrapers...")
    run_github_scraper()
    run_wappalyzer_scraper()
    check_and_notify()
    logger.info("✅ Cycle complet terminé")


# ─────────────────────────────────────────
# Scheduler
# ─────────────────────────────────────────
if __name__ == "__main__":
    init_db()

    scheduler = BlockingScheduler(timezone="America/Toronto")

    # GitHub — tous les jours à 08h00
    scheduler.add_job(
        run_github_scraper,
        CronTrigger(hour=8, minute=0),
        id="github_daily",
        name="Scraper GitHub quotidien"
    )

    # Wappalyzer — tous les jours à 08h30
    scheduler.add_job(
        run_wappalyzer_scraper,
        CronTrigger(hour=8, minute=30),
        id="wappalyzer_daily",
        name="Scraper Wappalyzer quotidien"
    )

    # Alertes email — tous les jours à 09h00
    scheduler.add_job(
        check_and_notify,
        CronTrigger(hour=9, minute=0),
        id="email_alerts",
        name="Alertes email quotidiennes"
    )

    # Rapport PDF — le 1er de chaque mois à 09h30
    scheduler.add_job(
        run_monthly_report,
        CronTrigger(day=1, hour=9, minute=30),
        id="monthly_report",
        name="Rapport PDF mensuel"
    )

    print("⏰ Scheduler démarré !")
    print("   → GitHub        : tous les jours à 08h00")
    print("   → Wappalyzer    : tous les jours à 08h30")
    print("   → Alertes email : tous les jours à 09h00")
    print("   → Rapport PDF   : le 1er de chaque mois à 09h30")
    print("   → CTRL+C pour arrêter\n")

    # Lance immédiatement une première fois au démarrage
    logger.info("🔁 Exécution immédiate au démarrage...")
    run_all()

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("🛑 Scheduler arrêté proprement")