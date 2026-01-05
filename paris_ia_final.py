import datetime
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters

# 🔹 Tes infos
API_KEY = "5c5cb9af7ca7fdd266d70692aa8d9a58"
BOT_TOKEN = "8235313223:AAGlU62C5YI6RNLaR_q9fIo2VfMv3yTTWAw"

API_URL = f"https://api.the-odds-api.com/v4/sports/nhl/odds/?apiKey={API_KEY}&regions=us&markets=h2h,spreads,totals"

# 🔹 Récupère les matchs NHL du jour
def fetch_nhl_matches():
    try:
        resp = requests.get(API_URL)
        data = resp.json()
        today = datetime.datetime.now(datetime.timezone.utc).date()
        matches_today = []

        for match in data:
            match_time = datetime.datetime.fromisoformat(match["commence_time"].replace("Z","+00:00"))
            if match_time.date() == today:
                matches_today.append(match)
        return matches_today
    except Exception as e:
        print("Erreur récupération NHL:", e)
        return []

# 🔹 Formate un match pour Telegram (1 seul pari par match)
def format_match(match):
    home = match.get("home_team", "Équipe 1")
    away = match.get("away_team", "Équipe 2")
    commence_time = match.get("commence_time", "Inconnu")

    try:
        markets = match["bookmakers"][0]["markets"]
        for market in markets:
            if market["key"] == "h2h":
                outcome = market["outcomes"][0]
                return f"{commence_time} - {home} vs {away}\n🎯 Pari recommandé: {outcome['name']} (cote approx: {outcome['price']})"
            elif market["key"] == "spreads":
                outcome = market["outcomes"][0]
                return f"{commence_time} - {home} vs {away}\n🎯 Handicap: {outcome['name']} {outcome.get('point', '')} (cote approx: {outcome['price']})"
            elif market["key"] == "totals":
                outcome = market["outcomes"][0]
                return f"{commence_time} - {home} vs {away}\n🎯 Totals: {outcome['name']} {outcome.get('point', '')} (cote approx: {outcome['price']})"
    except:
        return f"{commence_time} - {home} vs {away}\n⚠️ Aucun pari disponible"

# 🔹 Envoie les boutons automatiquement
async def send_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Pronostics", callback_data="pronostics")],
        [InlineKeyboardButton("Stats", callback_data="stats")],
        [InlineKeyboardButton("Bankroll", callback_data="bankroll")],
        [InlineKeyboardButton("Historique", callback_data="historique")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Bienvenue ! Choisissez une option :", reply_markup=reply_markup)

# 🔹 Gestion des boutons
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "pronostics":
        matches = fetch_nhl_matches()
        if not matches:
            message = f"🧪 NHL MACHINE À CASH\n📅 {datetime.datetime.now().strftime('%d/%m/%Y')}\n\n⚠️ Aucun match ou pronostic trouvé pour aujourd'hui."
        else:
            message = f"🧪 NHL MACHINE À CASH\n📅 {datetime.datetime.now().strftime('%d/%m/%Y')}\n\n"
            for m in matches:
                message += format_match(m) + "\n\n"
        await query.edit_message_text(message)

    elif query.data == "stats":
        await query.edit_message_text("📊 Statistiques: Prochainement...")

    elif query.data == "bankroll":
        await query.edit_message_text("💰 Bankroll: Prochainement...")

    elif query.data == "historique":
        await query.edit_message_text("🗂 Historique des pronostics: Prochainement...")

# 🔹 Lancement du bot
if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Boutons dès le premier message
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), send_buttons))
    
    # Gestion boutons
    app.add_handler(CallbackQueryHandler(button))

    app.run_polling()








