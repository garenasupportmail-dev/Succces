import os

# ============ ENVIRONMENT VARIABLES ============
BOT_TOKEN = os.environ.get('BOT_TOKEN')
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN environment variable is not set!")

OWNER_ID = int(os.environ.get('OWNER_ID', 8986441675))
CHANNEL_USERNAME = os.environ.get('CHANNEL_USERNAME', "@KALYUGESCROWSERVICE")
MAX_DEAL_LIMIT = 12000
DB_PATH = "data/escrow.db"

# ============ PREMIUM EMOJIS ============
PREMIUM_EMOJIS = {
    "verified": {"id": "6246537187614005254", "fallback": "✅"},
    "crown": {"id": "5794422335599546668", "fallback": "👑"},
    "shield": {"id": "6086778246882399112", "fallback": "🛡️"},
    "fire": {"id": "4956222745814762495", "fallback": "🔥"},
    "sparkle": {"id": "6010338729640596556", "fallback": "✨"},
    "star": {"id": "6244496562752331516", "fallback": "⭐"},
    "lock": {"id": "5433601609076586221", "fallback": "🔒"},
    "unlock": {"id": "5434064563601421981", "fallback": "🔓"},
    "check": {"id": "5977034395173715994", "fallback": "✅"},
    "cross": {"id": "5977028203127113755", "fallback": "❌"},
    "warning": {"id": "5463369591689987411", "fallback": "⚠️"},
    "info": {"id": "5463371706332570811", "fallback": "ℹ️"},
    "money": {"id": "6089104607328342288", "fallback": "💰"},
    "clock": {"id": "5433854239052935880", "fallback": "🕒"},
    "megaphone": {"id": "6035432248717147837", "fallback": "📢"},
    "wave": {"id": "6134450255637642537", "fallback": "👋"},
    "handshake": {"id": "6086753854958846976", "fallback": "🤝"},
    "diamond": {"id": "6086778246882399112", "fallback": "💎"},
    "rocket": {"id": "6086722893985317854", "fallback": "🚀"},
    "target": {"id": "6089151072758267766", "fallback": "🎯"},
    "trophy": {"id": "6089133937926864969", "fallback": "🏆"},
    "game": {"id": "6089222110495696270", "fallback": "🎮"},
}