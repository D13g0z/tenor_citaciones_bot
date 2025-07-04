import os
import logging
from flask import Flask, request
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from telegram.constants import ParseMode

from config import TOKEN
from respuestas import respuestas_legales
from respuestas_medioambiente import respuestas_medioambiente
from ayuda import generar_mensaje_ayuda

# --- Logging ---
logging.basicConfig(
    filename="errores.log",
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# --- Comandos ---
todos_los_comandos = {**respuestas_legales, **respuestas_medioambiente}

# --- Crear aplicación Telegram ---
application = ApplicationBuilder().token(TOKEN).build()

# --- Handlers ---
async def responder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if update.message and update.message.text:
            if update.message.chat.type not in ["group", "supergroup"]:
                return
            comando = update.message.text[1:].lower()
            mensaje = todos_los_comandos.get(comando)
            if mensaje:
                await update.message.reply_text(mensaje, parse_mode=ParseMode.MARKDOWN)
    except Exception as e:
        logging.error(f"Error en responder: {e}")

async def ayuda(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        mensaje = generar_mensaje_ayuda()
        await update.message.reply_text(mensaje, parse_mode=ParseMode.MARKDOWN)
    except Exception as e:
        logging.error(f"Error en ayuda: {e}")

async def estado(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ El bot está operativo y funcionando correctamente.")

# --- Registrar handlers ---
for cmd in todos_los_comandos:
    application.add_handler(CommandHandler(cmd, responder))

application.add_handler(CommandHandler("ayuda", ayuda))
application.add_handler(CommandHandler("estado", estado))

# --- Flask para recibir webhooks ---
flask_app = Flask(__name__)
WEBHOOK_SECRET = "webhookseguro"
WEBHOOK_PATH = f"/{WEBHOOK_SECRET}"
RENDER_URL = os.getenv("RENDER_EXTERNAL_URL")

@flask_app.route(WEBHOOK_PATH, methods=["POST"])
async def webhook():
    try:
        data = request.get_json(force=True)
        update = Update.de_json(data, application.bot)
        await application.process_update(update)
    except Exception as e:
        logging.error(f"Error en webhook: {e}")
    return "OK", 200

@flask_app.route("/health")
def health():
    return "OK", 200

# --- Configurar webhook en Telegram ---

if RENDER_URL:
    import asyncio
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(
        application.bot.set_webhook(url=f"{RENDER_URL}{WEBHOOK_PATH}")
    )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
flask_app.run(host="0.0.0.0", port=port)