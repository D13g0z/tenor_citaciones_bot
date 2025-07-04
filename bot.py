import os
import asyncio
import logging
from threading import Thread

from flask import Flask
from telegram.ext import ApplicationBuilder, CommandHandler
from telegram.constants import ParseMode

from config import TOKEN
from respuestas import respuestas_legales
from respuestas_medioambiente import respuestas_medioambiente
from ayuda import generar_mensaje_ayuda

# --- Configurar log de errores ---
logging.basicConfig(
    filename="errores.log",
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# --- Servidor Flask para mantener activo el servicio en Render ---
flask_app = Flask(__name__)

@flask_app.route("/health")
def health():
    return "OK", 200

def iniciar_flask():
    flask_app.run(host="0.0.0.0", port=10000)

# --- Unimos todos los comandos ---
todos_los_comandos = {**respuestas_legales, **respuestas_medioambiente}

# --- Función para responder comandos del diccionario ---
async def responder(update, context):
    try:
        if update.message.chat.type not in ["group", "supergroup"]:
            return  # Ignora mensajes fuera de grupos

        comando = update.message.text[1:].lower()
        mensaje = todos_los_comandos.get(comando)

        if mensaje:
            await update.message.reply_text(mensaje, parse_mode=ParseMode.MARKDOWN)

    except Exception as e:
        logging.error(f"Error en 'responder': {e}")

# --- Comando /ayuda accesible desde cualquier tipo de chat ---
async def ayuda(update, context):
    try:
        mensaje = generar_mensaje_ayuda()
        await update.message.reply_text(mensaje, parse_mode=ParseMode.MARKDOWN)
    except Exception as e:
        logging.error(f"Error en 'ayuda': {e}")

# --- Inicializamos el bot ---
async def iniciar_bot():
    app = ApplicationBuilder().token(TOKEN).build()

    for cmd in todos_los_comandos:
        app.add_handler(CommandHandler(cmd, responder))

    app.add_handler(CommandHandler("ayuda", ayuda))

    print("🤖 Bot activo. Escuchando comandos...")
    await app.run_polling()

# --- Ejecutar Flask + Bot en paralelo (sin usar asyncio.run) ---
if __name__ == "__main__":
    Thread(target=iniciar_flask).start()

    loop = asyncio.get_event_loop()
    loop.create_task(iniciar_bot())
    loop.run_forever()