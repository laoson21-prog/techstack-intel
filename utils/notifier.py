import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from loguru import logger
from utils.config import config

def send_alert_email(subject: str, html_body: str):
    """Envoie un email HTML d'alerte."""
    sender    = config.EMAIL_SENDER
    recipient = config.EMAIL_RECIPIENT
    password  = config.EMAIL_PASSWORD

    if not all([sender, recipient, password]):
        logger.warning("⚠️ Variables email manquantes dans .env — email non envoyé")
        return False

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"]    = sender
        msg["To"]      = recipient
        msg.attach(MIMEText(html_body, "html"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender, password)
            server.sendmail(sender, recipient, msg.as_string())

        logger.info(f"✅ Email envoyé : {subject}")
        return True

    except Exception as e:
        logger.error(f"❌ Erreur envoi email : {e}")
        return False


def build_alert_html(company_name: str, new_techs: list) -> str:
    """Génère le HTML de l'email d'alerte."""
    rows = ""
    for tech in new_techs:
        rows += f"""
        <tr>
            <td style="padding:10px 14px; border-bottom:1px solid #e2e8f0;">{tech['name']}</td>
            <td style="padding:10px 14px; border-bottom:1px solid #e2e8f0;">
                <span style="background:{'#ebf8ff' if tech['source']=='github' else '#e9d8fd'};
                             color:{'#2b6cb0' if tech['source']=='github' else '#553c9a'};
                             padding:2px 10px; border-radius:999px; font-size:12px;">
                    {tech['source']}
                </span>
            </td>
            <td style="padding:10px 14px; border-bottom:1px solid #e2e8f0; color:#718096;">
                {tech.get('category', '—')}
            </td>
        </tr>"""

    return f"""
    <html><body style="font-family:'Segoe UI',sans-serif; background:#f7fafc; padding:32px;">
        <div style="max-width:600px; margin:0 auto; background:white;
                    border-radius:12px; overflow:hidden; box-shadow:0 2px 8px rgba(0,0,0,0.1);">

            <div style="background:linear-gradient(135deg,#1a1f2e,#2d3748); padding:24px 32px;">
                <h1 style="color:#63b3ed; margin:0; font-size:1.4rem;">🔍 TechStack Intel</h1>
                <p style="color:#a0aec0; margin:6px 0 0;">Alerte — Nouvelle stack détectée</p>
            </div>

            <div style="padding:32px;">
                <h2 style="color:#2d3748; margin-bottom:8px;">🏢 {company_name}</h2>
                <p style="color:#718096; margin-bottom:24px;">
                    {len(new_techs)} nouvelle(s) technologie(s) détectée(s) lors du dernier scraping.
                </p>

                <table style="width:100%; border-collapse:collapse;">
                    <thead>
                        <tr style="background:#f7fafc;">
                            <th style="text-align:left; padding:10px 14px; color:#718096;
                                       font-size:12px; text-transform:uppercase;">Technologie</th>
                            <th style="text-align:left; padding:10px 14px; color:#718096;
                                       font-size:12px; text-transform:uppercase;">Source</th>
                            <th style="text-align:left; padding:10px 14px; color:#718096;
                                       font-size:12px; text-transform:uppercase;">Catégorie</th>
                        </tr>
                    </thead>
                    <tbody>{rows}</tbody>
                </table>

                <div style="margin-top:32px; padding:16px; background:#f7fafc;
                            border-radius:8px; text-align:center;">
                    <a href="http://localhost:5000/company/{company_name}"
                       style="color:#63b3ed; font-weight:600;">
                        Voir la stack complète →
                    </a>
                </div>
            </div>

            <div style="padding:16px 32px; background:#f7fafc; text-align:center;">
                <p style="color:#a0aec0; font-size:12px; margin:0;">
                    TechStack Intel — Rapport automatique
                </p>
            </div>
        </div>
    </body></html>
    """
