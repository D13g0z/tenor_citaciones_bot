import os
import logging
import asyncio
import difflib
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
BOT_VERSION = "1.0.1"
FECHA_ULTIMA_ACTUALIZACION = "2025-07-11"

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

#HEADLER COMANDO NO RECONOCIDO

async def comando_no_reconocido(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if update.message and update.message.chat.type in ["group", "supergroup"]:
            await update.message.reply_text(
                "⚠️ Comando no reconocido. Escribe /ayuda para ver los disponibles."
            )
    except Exception as e:
        logging.error(f"Error en comando_no_reconocido: {e}")

#HEADLER COMANDO AYUDA
async def ayuda(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        mensaje = generar_mensaje_ayuda()
        await update.message.reply_text(mensaje, parse_mode=ParseMode.MARKDOWN)
    except Exception as e:
        logging.error(f"Error en ayuda: {e}")

#HEADLER COMANDO ESTADO

async def estado(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        mensaje = "✅ El bot está operativo y funcionando correctamente."

        if hasattr(update, "callback_query"):
            await update.callback_query.message.reply_text(mensaje)
        else:
            await update.message.reply_text(mensaje)
    except Exception as e:
        logging.error(f"Error en /estado: {e}")

#HEADLER COMANDO DEBUG

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

#HEADLER COMANDO VERSION 

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

#HEARDLER LEYES        

async def leyes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        mensaje = "📚 *Acceso directo a las leyes referenciadas por el bot:*"
        teclado = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🚦 Ley de Tránsito", url="https://www.bcn.cl/leychile/navegar?idNorma=1007469"),
                InlineKeyboardButton("🍷 Ley de Alcoholes", url="https://www.bcn.cl/leychile/navegar?idNorma=1163383"),
            ],
            [
                InlineKeyboardButton("🌱 Ordenanza Medioambiente", url="https://www.bcn.cl/leychile/navegar?idNorma=1209493"),
                InlineKeyboardButton("🐶 Ordenanza Tenencia responsable", url="https://www.bcn.cl/leychile/navegar?i=265348"),
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

#HEADLER COMANDO MENU

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
        await leyes(update, context)
    elif opcion == "ver_comandos":
        await query.message.reply_text("📦 Escribe /ayuda o /version para ver los comandos disponibles.")
    elif opcion == "ver_estado":
        await estado(update, context)
    elif opcion.startswith("def:"):
        termino = opcion.split("def:")[1]
        definicion = definiciones.get(termino)
        if definicion:
            mensaje = f"📌 *{termino.replace('_', ' ').capitalize()}*\n{definicion}"
            await query.message.reply_text(mensaje, parse_mode=ParseMode.MARKDOWN)
        else:
            await query.message.reply_text("⚠️ No se encontró esa definición.")
    else:
        await query.message.reply_text("❓ Opción no reconocida.")

#HEADLER AUXILIAR DEFINICIONES 

def crear_handler_definicion(termino, definicion):
    async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            mensaje = f"📌 *{termino.replace('_', ' ').capitalize()}*\n{definicion}"
            await update.message.reply_text(mensaje, parse_mode=ParseMode.MARKDOWN)
        except Exception as e:
            logging.error(f"Error en definición {termino}: {e}")
    return handler

#HEADLER COMANDO BUSCAR

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

async def buscar_definicion(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if not context.args:
            await update.message.reply_text("🔍 Debes escribir una palabra. Ejemplo:\n`/buscar acera`", parse_mode=ParseMode.MARKDOWN)
            return

        consulta = " ".join(context.args).lower()
        sugerencias = []

        for termino in definiciones:
            if consulta in termino or consulta in definiciones[termino].lower():
                sugerencias.append(termino)

        if not sugerencias:
            aproximadas = difflib.get_close_matches(consulta, definiciones.keys(), n=5, cutoff=0.6)
            sugerencias.extend(aproximadas)

        if sugerencias:
            botones = []
            for s in sugerencias:
                nombre = s.replace("_", " ").capitalize()
                botones.append([InlineKeyboardButton(nombre, callback_data=f"def:{s}")])

            teclado = InlineKeyboardMarkup(botones)
            await update.message.reply_text("🔎 *Resultados encontrados:*", reply_markup=teclado, parse_mode=ParseMode.MARKDOWN)
        else:
            await update.message.reply_text("⚠️ No se encontró ningún término relacionado.", parse_mode=ParseMode.MARKDOWN)

    except Exception as e:
        logging.error(f"Error en /buscar: {e}")
        await update.message.reply_text("❌ Hubo un error al buscar la definición.")

# --- Registrar handlers ---

application.add_handler(CommandHandler("ayuda", ayuda))
application.add_handler(CommandHandler("estado", estado))
application.add_handler(CommandHandler("debug", debug))
application.add_handler(CommandHandler("version", version))
application.add_handler(CommandHandler("leyes", leyes))
application.add_handler(CommandHandler("menu", menu))
application.add_handler(CallbackQueryHandler(manejar_botones))
application.add_handler(CommandHandler("buscar", buscar_definicion))

# Cargar dinámicamente cada comando /def_<término>

for termino, definicion in definiciones.items():
    comando = f"def_{termino}"
    if len(comando) <= 32:  
        
        # Telegram command limit

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