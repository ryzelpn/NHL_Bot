import requests
import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

API_KEY = "5c5cb9af7ca7fdd266d70692aa8d9a58"
BOT_TOKEN = "8235313223:AAGlU62C5YI6RNLaR_q9fIo2VfMv3yTTWAw"
CHAT_ID = "5790502622"
MIN_COTE = 1.45

# Stockage simple pour l'exemple
historique = []
bankroll = {"solde": 1000.0}

# --- Fonction récupération pronostics NHL ---
def get_nhl_pronostics():
    url = f"https://api.the-odds-api.com/v4/sports/nhl/odds/?regions=us&markets=h2h,spreads,totals&apiKey={API_KEY}"
    try:
        res = requests.get(url).json()
        today = datetime.datetime.now().date()
        pronostics = []

        for match in res:
            # Vérifier la date du match
            commence = datetime.datetime.fromisoformat(match["commence_at"].replace("Z", "+00:00")).date()
            if commence != today:
                continue

            # Analyse simple pour choisir le pari le plus safe
            best_market = None
            best_odd = 0
            description = ""
            for bookmaker in match.get("bookmakers", []):
                for market in bookmaker.get("markets", []):
                    if market["key"] == "h2h":
                        for outcome in market["outcomes"]:
                            cote = outcome["price"]
                            if cote >= MIN_COTE and cote > best_odd:
                                best_odd = cote
                                best_market = "Victoire"
                                description = f"{outcome['name']} (cote approx: {cote})"
                    elif market["key"] == "spreads":
                        for outcome in market["outcomes"]:
                            cote = outcome["price"]
                            handicap = outcome.get("point", 0)
                            if cote >= MIN_COTE and cote > best_odd:
                                best_odd = cote
                                best_market = "Handicap"
                                description = f"{outcome['name']} ({handicap:+} buts, cote approx: {cote})"
                    elif market["key"] == "totals":
                        for outcome in market["outcomes"]:
                            cote = outcome["price"]
                            total = outcome.get("total", 0)
                            type_total = outcome.get("name", "")
                            if cote >= MIN_COTE and cote > best_odd:
                                best_odd = cote
                                best_market = "Total"
                                description = f"{type_total} {total} buts (cote approx: {cote})"
            if best_market:
                pronostics.append({
                    "heure": datetime.datetime.fromisoformat(match["commence_at"].replace("Z", "+00:00")).strftime("%H:%M"),
                    "match": f"{match['home_team']} vs {match['away_team']}",
                    "paris": description
                })
        return pronostics
    except Exception as e:
        return [{"match": "Erreur NHL", "paris": str(e)}]

# --- Fonctions Telegram ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Pronostics", callback_data='pronostics')],
        [InlineKeyboardButton("Stats", callback_data='stats')],
        [InlineKeyboardButton("Bankroll", callback_data='bankroll')],
        [InlineKeyboardButton("Historique", callback_data='historique')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Bienvenue sur NHL MACHINE À CASH V5 ! Choisissez une option :', reply_markup=reply_markup)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "pronostics":
        pronos = get_nhl_pronostics()
        if not pronos:
            message = f"⚠️ Aucun pronostic trouvé pour aujourd'hui ({datetime.datetime.now().strftime('%d/%m/%Y')})"
        else:
            message = f"🏒 NHL MACHINE À CASH\n📅 {datetime.datetime.now().strftime('%d/%m/%Y')}\n\n"
            for p in pronos:
                message += f"{p['heure']} - {p['match']}\n🎯 {p['paris']}\n\n"
        await query.message.reply_text(message)
    elif query.data == "stats":
        message = f"📊 Statistiques bot :\nPronostics envoyés : {len(historique)}\n"
        await query.message.reply_text(message)
    elif query.data == "bankroll":
        message = f"💰 Bankroll : {bankroll['solde']}€"
        await query.message.reply_text(message)
    elif query.data == "historique":
        if not historique:
            await query.message.reply_text("Aucun historique pour l'instant.")
        else:
            message = "📝 Historique des pronostics :\n"
            for h in historique[-10:]:
                message += f"{h}\n"
            await query.message.reply_text(message)

# --- Lancer bot ---
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button))

print("Bot NHL MACHINE À CASH lancé !")
app.run_polling()








