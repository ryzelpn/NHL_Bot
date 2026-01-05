import logging
import requests
from datetime import datetime, timezone
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CallbackQueryHandler
)

# ================== CONFIG ==================
BOT_TOKEN = "8235313223:AAGlU62C5YI6RNLaR_q9fIo2VfMv3yTTWAw"
CHAT_ID = "5790502622"
ODDS_API_KEY = "5c5cb9af7ca7fdd266d70692aa8d9a58"

NHL_ENDPOINT = "https://api.the-odds-api.com/v4/sports/icehockey_nhl/odds"
MIN_ODDS = 1.45

logging.basicConfig(level=logging.INFO)

# ================== NHL DATA ==================
def get_nhl_matches():
    params = {
        "apiKey": ODDS_API_KEY,
        "regions": "eu",
        "markets": "h2h",
        "oddsFormat": "decimal"
    }
    r = requests.get(NHL_ENDPOINT, params=params, timeout=10)
    if r.status_code != 200:
        return []

    data = r.json()
    today = datetime.now(timezone.utc).date()
    matches = []

    for match in data:
        start = datetime.fromisoformat(match["commence_time"].replace("Z", "+00:00"))
        if start.date() != today:
            continue

        home = match["home_team"]
        away = match["away_team"]

        for bookmaker in match["bookmakers"]:
            for market in bookmaker["markets"]:
                for outcome in market["outcomes"]:
                    if outcome["price"] >= MIN_ODDS:
                        matches.append({
                            "time": start.strftime("%H:%M"),
                            "match": f"{home} vs {away}",
                            "pick": outcome["name"],
                            "odds": outcome["price"]
                        })
                        break
                break
            break

    return matches

# ================== MESSAGE ==================
def format_message():
    picks = get_nhl_matches()
    today = datetime.now(timezone.utc).strftime("%d/%m/%Y")

    if not picks:
        return f"🏒 NHL MACHINE À CASH\n📅 {today}\n\n⚠️ Aucun pari détecté aujourd'hui."

    msg = f"🏒 NHL MACHINE À CASH\n📅 {today}\n\n"
    for p in picks[:5]:
        msg += (
            f"⏰ {p['time']}\n"
            f"🏒 {p['match']}\n"
            f"🎯 Victoire : {p['pick']}\n"
            f"💰 Cote : {p['odds']}\n\n"
        )
    return msg

# ================== BUTTONS ==================
async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📊 Pronostics NHL", callback_data="pronostics")],
        [InlineKeyboardButton("💰 Bankroll", callback_data="bankroll")],
        [InlineKeyboardButton("📈 Stats", callback_data="stats")]
    ]
    await update.callback_query.message.reply_text(
        "📌 MENU PRINCIPAL",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "pronostics":
        await query.message.reply_text(format_message())
    elif query.data == "bankroll":
        await query.message.reply_text("💰 Gestion bankroll : mise fixe recommandée (1–3%).")
    elif query.data == "stats":
        await query.message.reply_text("📈 Stats en cours de construction.")

# ================== MAIN ==================
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CallbackQueryHandler(handle_buttons))
    app.add_handler(CallbackQueryHandler(menu, pattern="^$"))

    app.run_polling()

if __name__ == "__main__":
    main()




