import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.database import get_company_stack, get_all_companies
from datetime import datetime

def generate_html_report():
    companies = get_all_companies()
    date = datetime.now().strftime("%d/%m/%Y à %H:%M")

    rows = ""
    for company in companies:
        name   = company[1]
        domain = company[2]
        stack  = get_company_stack(name)

        langs  = [r[0] for r in stack if r[2] == "Language"]
        topics = [r[0] for r in stack if r[2] == "Topic"]

        lang_badges  = "".join([f'<span class="badge lang">{l}</span>' for l in langs[:6]])
        topic_badges = "".join([f'<span class="badge topic">{t}</span>' for t in topics[:6]])

        rows += f"""
        <tr>
            <td><strong>{name}</strong><br><small>{domain}</small></td>
            <td>{lang_badges}</td>
            <td>{topic_badges}</td>
        </tr>
        """

    html = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>TechStack Intel — Rapport</title>
    <style>
        body {{ font-family: Arial, sans-serif; background: #0f172a; color: #e2e8f0; padding: 40px; }}
        h1   {{ color: #38bdf8; }}
        p    {{ color: #94a3b8; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
        th   {{ background: #1e293b; padding: 12px; text-align: left; color: #38bdf8; }}
        td   {{ padding: 12px; border-bottom: 1px solid #1e293b; vertical-align: top; }}
        tr:hover td {{ background: #1e293b; }}
        .badge {{ display: inline-block; padding: 4px 10px; border-radius: 20px;
                  font-size: 12px; margin: 2px; }}
        .lang  {{ background: #0369a1; color: #fff; }}
        .topic {{ background: #065f46; color: #fff; }}
    </style>
</head>
<body>
    <h1>🔍 TechStack Intel</h1>
    <p>Rapport généré le {date}</p>
    <table>
        <thead>
            <tr>
                <th>🏢 Entreprise</th>
                <th>💻 Langages</th>
                <th>🏷️ Topics</th>
            </tr>
        </thead>
        <tbody>
            {rows}
        </tbody>
    </table>
</body>
</html>"""

    os.makedirs("reports", exist_ok=True)
    path = "reports/report.html"
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"✅ Rapport généré : {path}")
    print(f"👉 Ouvre-le dans ton navigateur !")

if __name__ == "__main__":
    generate_html_report()
