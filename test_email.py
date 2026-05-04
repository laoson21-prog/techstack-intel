import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from utils.notifier import send_alert_email, build_alert_html

# Données de test
test_techs = [
    {"name": "React",      "source": "wappalyzer", "category": "JavaScript frameworks"},
    {"name": "TypeScript", "source": "github",     "category": "Language"},
    {"name": "Next.js",    "source": "wappalyzer", "category": "Web frameworks"},
]

html = build_alert_html("Vercel", test_techs)
result = send_alert_email(
    subject="🔍 TechStack Intel — Test d'alerte",
    html_body=html
)

if result:
    print("✅ Email envoyé avec succès !")
else:
    print("❌ Échec — vérifie ton .env")
