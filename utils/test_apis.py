import requests
import os
from dotenv import load_dotenv
from Wappalyzer import Wappalyzer, WebPage

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

# ─────────────────────────────────────────
# TEST 1 : GITHUB
# ─────────────────────────────────────────
def test_github():
    print("=" * 50)
    print("🔍 TEST GITHUB API")
    print("=" * 50)

    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }

    # Test 1 : Vérifier le token
    r = requests.get("https://api.github.com/user", headers=headers)
    if r.status_code == 200:
        user = r.json()
        print(f"✅ Connecté en tant que : {user['login']}")
    else:
        print(f"❌ Erreur token : {r.status_code}")
        return

    # Test 2 : Récupérer la stack de Shopify
    print("\n🔍 Test récupération stack Shopify...")
    r2 = requests.get(
        "https://api.github.com/orgs/Shopify/repos?per_page=5&sort=stars",
        headers=headers
    )
    if r2.status_code == 200:
        repos = r2.json()
        print(f"✅ {len(repos)} repos récupérés pour Shopify :")
        for repo in repos:
            print(f"   → {repo['name']} | Lang: {repo.get('language', 'N/A')} | ⭐ {repo['stargazers_count']}")
    else:
        print(f"❌ Erreur repos : {r2.status_code}")

    # Test 3 : Langages utilisés
    print("\n🔍 Langages détectés chez Shopify...")
    r3 = requests.get(
        "https://api.github.com/repos/Shopify/shopify-app-js/languages",
        headers=headers
    )
    if r3.status_code == 200:
        langs = r3.json()
        print(f"✅ Langages : {list(langs.keys())}")
    else:
        print(f"❌ Erreur langages : {r3.status_code}")

# ─────────────────────────────────────────
# TEST 2 : WAPPALYZER LOCAL
# ─────────────────────────────────────────
def test_wappalyzer():
    print("\n" + "=" * 50)
    print("🔍 TEST WAPPALYZER LOCAL")
    print("=" * 50)

    try:
        wappalyzer = Wappalyzer.latest()
        webpage    = WebPage.new_from_url("https://stripe.com")
        techs      = wappalyzer.analyze(webpage)

        print(f"✅ Wappalyzer OK — Stack de stripe.com :")
        for tech in list(techs)[:10]:
            print(f"   → {tech}")

    except Exception as e:
        print(f"❌ Erreur Wappalyzer : {e}")

# ─────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────
if __name__ == "__main__":
    test_github()
    test_wappalyzer()
    print("\n" + "=" * 50)
    print("🏁 Tests terminés")
    print("=" * 50)
