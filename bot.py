import os
import logging
import asyncio
from datetime import datetime
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)
from telegram.constants import ParseMode

from config import TOKEN
from respuestas import respuestas_legales
from respuestas_medioambiente import respuestas_medioambiente
from ayuda import generar_mensaje_ayuda
from definiciones import definiciones  # ✅ NUEVO

# --- Logging ---
logging.basicConfig(
    filename="errores.log",
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# --- Metadatos del bot ---
BOT_VERSION = "1.0.0"
FECHA_ULTIMA_ACTUALIZACION = "2025-07-06"

# --- Comandos disponibles ---
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

async def comando_no_reconocido(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if update.message and update.message.chat.type in ["group", "supergroup"]:
            await update.message.reply_text(
                "⚠️ Comando no reconocido. Escribe /ayuda para ver los disponibles."
            )
    except Exception as e:
        logging.error(f"Error en comando_no_reconocido: {e}")

async def ayuda(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        mensaje = generar_mensaje_ayuda()
        await update.message.reply_text(mensaje, parse_mode=ParseMode.MARKDOWN)
    except Exception as e:
        logging.error(f"Error en ayuda: {e}")

async def estado(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ El bot está operativo y funcionando correctamente.")

async def debug(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if update.message:
            user = update.message.from_user
            chat = update.message.chat
            text = update.message.text

            print("📥 Nuevo update recibido:", flush=True)
            print(f"👤 Usuario: {user.full_name} (ID: {user.id})", flush=True)
            print(f"💬 Mensaje: {text}", flush=True)
            print(f"👥 Chat ID: {chat.id} | Tipo: {chat.type}", flush=True)

            await update.message.reply_text("🛠️ Debug recibido. Revisa la consola.")
    except Exception as e:
        logging.error(f"Error en /debug: {e}")

async def version(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        total = len(todos_los_comandos)
        mensaje = (
            f"🤖 *Tenor Citaciones Bot*\n"
            f"📦 *Versión:* {BOT_VERSION}\n"
            f"📅 *Actualización:* {FECHA_ULTIMA_ACTUALIZACION}\n"
            f"🔢 *Comandos activos:* {total}\n"
            f"👤 *Autor:* Diego Zúñiga"
        )
        await update.message.reply_text(mensaje, parse_mode=ParseMode.MARKDOWN)
    except Exception as e:
        logging.error(f"Error en /version: {e}")

#Mostrar definiciones

async def mostrar_definiciones(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        lista = "\n".join([f"/def_{k}" for k in sorted(definiciones)])
        mensaje = (
            "📘 *Diccionario de Términos Legales*\n\n"
            "Escribe alguno de estos comandos para ver su definición completa:\n\n"
            f"{lista}"
        )
        await update.message.reply_text(mensaje, parse_mode=ParseMode.MARKDOWN)
    except Exception as e:
        logging.error(f"Error en /def: {e}")

# ✅ NUEVO: Generar handlers dinámicos para definiciones
def crear_handler_definicion(termino, definicion):
    async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            mensaje = f"📌 *{termino.replace('_', ' ').capitalize()}*\n{definicion}"
            await update.message.reply_text(mensaje, parse_mode=ParseMode.MARKDOWN)
        except Exception as e:
            logging.error(f"Error en definición {termino}: {e}")
    return handler

# --- Registrar handlers ---
for cmd in todos_los_comandos:
    application.add_handler(CommandHandler(cmd, responder))

application.add_handler(CommandHandler("ayuda", ayuda))
application.add_handler(CommandHandler("estado", estado))
application.add_handler(CommandHandler("debug", debug))
application.add_handler(CommandHandler("version", version))
application.add_handler(CommandHandler("def", mostrar_definiciones))

for termino, definicion in definiciones.items():
    comando = f"def_{termino}"
    application.add_handler(CommandHandler(comando, crear_handler_definicion(termino, definicion)))

# 🧱 Fallback para comandos no reconocidos
application.add_handler(MessageHandler(filters.COMMAND, comando_no_reconocido))

# --- Ejecución por consola ---
if __name__ == "__main__":
    print("🚀 Iniciando bot...", flush=True)
    asyncio.run(application.run_polling())