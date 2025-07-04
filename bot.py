import os
import logging
from flask import Flask, request
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler,
    filters
)
from telegram.constants import ParseMode

from config import TOKEN
from respuestas import respuestas_legales
from respuestas_medioambiente import respuestas_medioambiente
from ayuda import generar_mensaje_ayuda

# --- Logging de errores ---
logging.basicConfig(
    filename="errores.log",
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# --- Cargar comandos ---
todos_los_comandos = {**respuestas_legales, **respuestas_medioambiente}

# --- Crear aplicación Telegram ---
app_telegram = ApplicationBuilder().token(TOKEN).build()

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
    try:
        await update.message.reply_text("✅ El bot está operativo y funcionando correctamente.")
    except Exception as e:
        logging.error(f"Error en estado: {e}")

# --- Agregar handlers ---
for cmd in todos_los_comandos:
    app_telegram.add_handler(CommandHandler(cmd, responder))

app_telegram.add_handler(CommandHandler("ayuda", ayuda))
app_telegram.add_handler(CommandHandler("estado", estado))

# --- Configurar Webhook ---
flask_app = Flask(__name__)
WEBHOOK_SECRET = "miwebhookseguro"
RENDER_URL = os.getenv("RENDER_EXTERNAL_URL", "https://TU_DOMINIO_RENDER.onrender.com")
WEBHOOK_PATH = f"/{WEBHOOK_SECRET}"

@app_telegram.webhook(path=WEBHOOK_PATH)
async def webhook_handler(update: Update):
    await app_telegram.process_update(update)

@flask_app.route("/health")
def health():
    return "OK", 200

@flask_app.before_first_request
def configurar_webhook():
    app_telegram.bot.set_webhook(
        url=f"{RENDER_URL}{WEBHOOK_PATH}"
    )

if __name__ == "__main__":
    flask_app.run(port=10000)