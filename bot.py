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
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackQueryHandler
from definiciones import definiciones


# --- Logging ---
logging.basicConfig(
    filename="errores.log",
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# --- Metadatos del bot ---
BOT_VERSION = "1.0.0"
FECHA_ULTIMA_ACTUALIZACION = "2025-07-06"

# --- Comandos base ---
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

#Head Estado 

async def estado(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        mensaje = "✅ El bot está operativo y funcionando correctamente."

        if hasattr(update, "callback_query"):
            await update.callback_query.message.reply_text(mensaje)
        else:
            await update.message.reply_text(mensaje)
    except Exception as e:
        logging.error(f"Error en /estado: {e}")

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

#head LEYES        

async def leyes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        mensaje = "📚 *Acceso directo a las leyes referenciadas por el bot:*"
        teclado = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🚦 Ley de Tránsito", url="https://www.bcn.cl/leychile/navegar?idNorma=200109"),
                InlineKeyboardButton("🍷 Ley de Alcoholes", url="https://www.bcn.cl/leychile/navegar?idNorma=30685"),
            ],
            [
                InlineKeyboardButton("🌱 Ley del Medioambiente", url="https://www.bcn.cl/leychile/navegar?idNorma=30667"),
            ]
        ])

        if hasattr(update, "callback_query"):
            await update.callback_query.message.reply_text(
                mensaje,
                reply_markup=teclado,
                parse_mode=ParseMode.MARKDOWN
            )
        else:
            await update.message.reply_text(
                mensaje,
                reply_markup=teclado,
                parse_mode=ParseMode.MARKDOWN
            )

    except Exception as e:
        logging.error(f"Error en /leyes: {e}")

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if update.message.chat.type not in ["group", "supergroup"]:
            return

        teclado = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("📘 Leyes", callback_data="ver_leyes"),
                InlineKeyboardButton("📦 Comandos", callback_data="ver_comandos")
            ],
            [
                InlineKeyboardButton("ℹ️ Estado", callback_data="ver_estado")
            ]
        ])

        mensaje = "🔧 *Menú Principal del Bot*\n\nElige una opción:"
        await update.message.reply_text(mensaje, reply_markup=teclado, parse_mode=ParseMode.MARKDOWN)
    except Exception as e:
        logging.error(f"Error en /menu: {e}")

async def manejar_botones(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    opcion = query.data

    if opcion == "ver_leyes":
        await leyes(update, context)  # Usa el handler que ya tenés
    elif opcion == "ver_comandos":
        await query.message.reply_text("📦 Escribe /ayuda o /version para ver los comandos disponibles.")
    elif opcion == "ver_estado":
        await estado(update, context)
    else:
        await query.message.reply_text("❓ Opción no reconocida.")

#HEADLER DEFINICIONES 

async def mostrar_definiciones(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if update.message.chat.type not in ["group", "supergroup"]:
            return
        comandos = sorted([f"/def_{k}" for k in definiciones.keys()])
        lista = "\n".join(comandos)
        mensaje = (
            "📘 *Diccionario de Definiciones Legales Art: 2 ley de transito*\n\n"
            "Estos son los comandos disponibles para consultar términos legales:\n\n"
            f"{lista}\n\n"
            "✏️ Escribe uno de ellos para ver su definición."
        )
        await update.message.reply_text(mensaje, parse_mode=ParseMode.MARKDOWN)
    except Exception as e:
        logging.error(f"Error en /def: {e}")

def crear_handler_definicion(termino, definicion):
    async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            mensaje = f"📌 *{termino.replace('_', ' ').capitalize()}*\n{definicion}"
            await update.message.reply_text(mensaje, parse_mode=ParseMode.MARKDOWN)
        except Exception as e:
            logging.error(f"Error en definición {termino}: {e}")
    return handler        


# --- Registrar handlers ---

application.add_handler(CommandHandler("ayuda", ayuda))
application.add_handler(CommandHandler("estado", estado))
application.add_handler(CommandHandler("debug", debug))
application.add_handler(CommandHandler("version", version))
application.add_handler(CommandHandler("leyes", leyes))
application.add_handler(CommandHandler("menu", menu))
application.add_handler(CallbackQueryHandler(manejar_botones))

# /def muestra la lista de definiciones disponibles
application.add_handler(CommandHandler("def", mostrar_definiciones))

# Cargar dinámicamente cada comando /def_<término>
for termino, definicion in definiciones.items():
    comando = f"def_{termino}"
    if len(comando) <= 32:  # Telegram command limit
        application.add_handler(CommandHandler(comando, crear_handler_definicion(termino, definicion)))
    else:
        logging.warning(f"⚠️ Comando demasiado largo y no registrado: {comando}")

for cmd in todos_los_comandos:
    application.add_handler(CommandHandler(cmd, responder))

application.add_handler(MessageHandler(filters.COMMAND, comando_no_reconocido))

# --- Ejecución por consola ---
if __name__ == "__main__":
    print("🚀 Iniciando bot...", flush=True)
    asyncio.run(application.run_polling()) 