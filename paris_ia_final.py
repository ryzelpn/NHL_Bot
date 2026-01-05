import datetime
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler

# ------------------ CONFIG ------------------
BOT_TOKEN = "8235313223:AAGlU62C5YI6RNLaR_q9fIo2VfMv3yTTWAw"
CHAT_ID = "5790502622"
API_KEY = "5c5cb9af7ca7fdd266d70692aa8d9a58"
TIMEZONE_OFFSET = 1  # Europe/Paris

# ------------------ FONCTIONS NHL ------------------
def get_nhl_matches():
    """Récupère les matchs NHL du jour et retourne une liste de dict"""
    url = f"https://api.the-odds-api.com/v4/sports/icehockey_nhl/odds/?apiKey={API_KEY}&regions=us&markets=h2h,spreads,totals"
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
    except Exception as e:
        print(f"Erreur récupération NHL: {e}")
        return []

    matches_today = []
    now = datetime.datetime.utcnow() + datetime.timedelta(hours=TIMEZONE_OFFSET)
    today = now.date()

    for match in data:
        try:
            start_time_str = match.get("commence_time")
            start_time = datetime.datetime.fromisoformat(start_time_str.replace("Z", "+00:00")).astimezone()
            if start_time.date() != today:
                continue  # on prend que les matchs du jour

            home_team = match.get("home_team")
            away_team = match.get("away_team")

            # Cherche le marché "spreads" ou "totals" le plus safe
            best_market = None
            for market in match.get("bookmakers", []):
                for m in market.get("markets", []):
                    if m["key"] in ["spreads", "totals", "h2h"]:
                        best_market = m
                        break
                if best_market:
                    break

            if not best_market:
                continue

            matches_today.append({
                "home": home_team,
                "away": away_team,
                "start": start_time.strftime("%H:%M"),
                "market": best_market
            })

        except Exception as e:
            print(f"Erreur traitement match NHL: {e}")
            continue

    return matches_today

def format_nhl_message(matches):
    """Formate les matchs pour Telegram"""
    if not matches:
        return "🏒 NHL MACHINE À CASH\n📅 {}\n\n⚠️ Aucun match ou pronostic trouvé pour aujourd'hui.".format(
            (datetime.datetime.utcnow() + datetime.timedelta(hours=TIMEZONE_OFFSET)).strftime("%d/%m/%Y")
        )

    msg = "🏒 NHL MACHINE À CASH\n📅 {}\n\n".format(
        (datetime.datetime.utcnow() + datetime.timedelta(hours=TIMEZONE_OFFSET)).strftime("%d/%m/%Y")
    )

    for m in matches:
        market_type = m["market"]["key"].capitalize()
        msg += f"{m['start']} - {m['home']} vs {m['away']}\n🎯 Marché: {market_type}\n\n"

    return msg

# ------------------ BOT TELEGRAM ------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Message d'accueil avec menu principal"""
    keyboard = [
        [InlineKeyboardButton("📊 Statistiques", callback_data="stats")],
        [InlineKeyboardButton("💰 Bankroll", callback_data="bankroll")],
        [InlineKeyboardButton("🏒 Pronostics NHL", callback_data="pronostics")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Bienvenue dans NHL Machine à Cash ! Choisissez une option :", reply_markup=reply_markup)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gère les boutons"""
    query = update.callback_query
    await query.answer()

    if query.data == "pronostics":
        matches = get_nhl_matches()
        msg = format_nhl_message(matches)

        keyboard = [[InlineKeyboardButton("🔙 Retour", callback_data="menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(msg, reply_markup=reply_markup)

    elif query.data == "stats":
        # Exemple fictif de stats
        msg = "📊 Statistiques du bot :\n\n- Pronostics passés : 15/20\n- Victoires : 75%\n- Cote moyenne : 1.52"
        keyboard = [[InlineKeyboardButton("🔙 Retour", callback_data="menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(msg, reply_markup=reply_markup)

    elif query.data == "bankroll":
        # Exemple fictif de bankroll
        msg = "💰 Bankroll actuelle : 500€\n- Mise totale aujourd'hui : 20€\n- Gains estimés : 18€"
        keyboard = [[InlineKeyboardButton("🔙 Retour", callback_data="menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(msg, reply_markup=reply_markup)

    elif query.data == "menu":
        keyboard = [
            [InlineKeyboardButton("📊 Statistiques", callback_data="stats")],
            [InlineKeyboardButton("💰 Bankroll", callback_data="bankroll")],
            [InlineKeyboardButton("🏒 Pronostics NHL", callback_data="pronostics")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("Bienvenue dans NHL Machine à Cash ! Choisissez une option :", reply_markup=reply_markup)

async def pronostics_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Permet de demander les pronostics via /pronostics"""
    matches = get_nhl_matches()
    msg = format_nhl_message(matches)
    await update.message.reply_text(msg)

# ------------------ LANCEMENT ------------------
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("pronostics", pronostics_command))
    app.add_handler(CallbackQueryHandler(button))

    app.run_polling()

if __name__ == "__main__":
    main()







