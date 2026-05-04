# utils/affiliate_links.py

AFFILIATE_LINKS = {
    "vercel":       {"url": "https://vercel.com/?ref=TON_ID",       "label": "🚀 Hébergez comme eux",      "commission": "100$"},
    "netlify":      {"url": "https://netlify.com/?ref=TON_ID",      "label": "⚡ Déployez sur Netlify",    "commission": "50$"},
    "digitalocean": {"url": "https://digitalocean.com/?ref=TON_ID", "label": "☁️ Essayez DigitalOcean",    "commission": "100$"},
    "shopify":      {"url": "https://shopify.com/?ref=TON_ID",      "label": "🛒 Lancez votre boutique",   "commission": "20% récurrent"},
    "supabase":     {"url": "https://supabase.com/?ref=TON_ID",     "label": "🗄️ Base de données moderne", "commission": "30%"},
    "mongodb":      {"url": "https://mongodb.com/?ref=TON_ID",      "label": "🍃 Essayez MongoDB Atlas",   "commission": "50$"},
    "github":       {"url": "https://github.com/?ref=TON_ID",       "label": "🐙 GitHub Copilot",          "commission": "20$"},
    "notion":       {"url": "https://notion.so/?ref=TON_ID",        "label": "📝 Essayez Notion",          "commission": "50% / 1 an"},
    "stripe":       {"url": "https://stripe.com/?ref=TON_ID",       "label": "💳 Paiements avec Stripe",   "commission": "variable"},
    "next.js":      {"url": "https://vercel.com/?ref=TON_ID",       "label": "⚡ Hébergez votre Next.js",  "commission": "100$"},
    "react":        {"url": "https://vercel.com/?ref=TON_ID",       "label": "⚛️ Déployez votre React",    "commission": "100$"},
    "heroku":       {"url": "https://heroku.com/?ref=TON_ID",       "label": "🌐 Déployez sur Heroku",     "commission": "50$"},
    "aws":          {"url": "https://aws.amazon.com/?ref=TON_ID",   "label": "☁️ Démarrez sur AWS",        "commission": "25% récurrent"},
    "cloudflare":   {"url": "https://cloudflare.com/?ref=TON_ID",   "label": "🔒 Protégez votre site",     "commission": "100$"},
    "planetscale":  {"url": "https://planetscale.com/?ref=TON_ID",  "label": "🪐 Base MySQL scalable",     "commission": "30$"},
}

def get_affiliate(tech_name: str):
    """Retourne le lien affilié pour une technologie donnée."""
    return AFFILIATE_LINKS.get(tech_name.lower(), None)
