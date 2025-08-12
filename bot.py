import os
import logging
import asyncio
import difflib
from difflib import get_close_matches
from datetime import datetime
from telegram import Update
from telegram.ext import (
    ApplicationHandlerStop,
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
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
from definiciones_ley import definiciones
from categorias import categorias
from cuadrantes import cuadrantes



definiciones = {
    **respuestas_legales,
    **respuestas_medioambiente,
    **definiciones
}

# --- Logging ---

logging.basicConfig(
    filename="errores.log",
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# --- Metadatos del bot ---

BOT_VERSION = "1.1.0"
FECHA_ULTIMA_ACTUALIZACION = "2025-08-12"

# --- Comandos base ---

todos_los_comandos = {**respuestas_legales, **respuestas_medioambiente}

# --- Crear aplicación Telegram ---

application = ApplicationBuilder().token(TOKEN).build()

# --- Handlers configuracion  ---

async def responder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if update.message and update.message.text:
            comando = update.message.text[1:].lower()
            mensaje = todos_los_comandos.get(comando)
            if mensaje:
                await update.message.reply_text(mensaje, parse_mode=ParseMode.MARKDOWN)
    except Exception as e:
        logging.error(f"Error en responder: {e}")


#HEADLER ID

async def obtener_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    mensaje = f"🆔 El ID de este grupo es:\n`{chat.id}`"
    await update.message.reply_text(mensaje, parse_mode=ParseMode.MARKDOWN)

#HEADLER BIENVENIDA

async def bienvenida_nuevo_miembro(update: Update, context: ContextTypes.DEFAULT_TYPE):
    nuevos_usuarios = update.message.new_chat_members
    for usuario in nuevos_usuarios:
        nombre = usuario.full_name
        await update.message.reply_text(
            f"🌟 ¡Hola {nombre}, bienvenido/a al grupo!\n\n"
            f"Soy *Diego Zúñiga*, creador del bot, y me alegra que te unas.\n\n"
            f"🤖 Este bot fue desarrollado para ayudarte a entender de forma clara y rápida distintas normas legales, ordenanzas municipales y temas ciudadanos que pueden ser útiles en nuestro trabajo día a día.\n\n"
            f"📌 Para comenzar, solo escribe el comando `/menu`. Desde ahí podrás explorar categorías como tránsito, medio ambiente, documentación y más.\n\n"
            f"Espero que esta herramienta te resulte práctica y que te acompañe cuando necesites información confiable.\n\n"
            f"¡Bienvenido/a nuevamente, y que tengas una excelente experiencia!",
            parse_mode="Markdown"
        )


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
        mensaje = (
    "✅ Estado del bot: operativo\n\n"
    f"🧩 Comandos cargados: {len(todos_los_comandos)}\n"
    f"📅 Última actualización: {FECHA_ULTIMA_ACTUALIZACION}\n"
    f"🔢 Versión: {BOT_VERSION}"
)

        if update.callback_query:
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

#HEARLER ANUNCIAR PRUEBAS

import logging
from datetime import datetime
from telegram.constants import ParseMode

# ID del administrador autorizado
ADMIN_ID = 1160883568 #Id Diego Zúñiga
# Lista de grupos donde se enviará el anuncio
CHAT_IDS_PRUEBA = [1002781860922]
async def avisar_prueba_comandos(context: ContextTypes.DEFAULT_TYPE):
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M")
    mensaje = (
        f"🚀 *¡Prueba masiva activada!*\n🕒 {fecha}\n\n"
        "Durante este período estaremos evaluando todos los comandos disponibles del bot.\n"
        "Usa `/menu` para navegar por temas como Tránsito 🚦 y Medioambiente 🌱.\n"
        "Reporta errores o sugerencias usando el canal correspondiente. ¡Gracias por participar! 🙌"
    )

    for chat_id in CHAT_IDS_PRUEBA:
        try:
            await context.bot.send_message(chat_id=chat_id, text=mensaje, parse_mode=ParseMode.MARKDOWN)
            logging.info(f"✅ Mensaje de prueba enviado a grupo {chat_id}")
        except Exception as e:
            logging.error(f"❌ Error al enviar mensaje a {chat_id}: {e}")

async def anunciar_prueba(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("⚠️ No tenés permiso para ejecutar este comando.")
        return

    await avisar_prueba_comandos(context)
    await update.message.reply_text("📢 Mensaje enviado a todos los grupos.")
    
# HANDLER MANEJO DE BOTONES

# Función de generar botones categoria transito

def generar_botones_categorias_transito(categorias_legales_transito):
    botones = []
    for categoria in categorias_legales_transito:
        nombre = categoria.replace("_", " ").capitalize()
        botones.append([InlineKeyboardButton(nombre, callback_data=f"categoria:{categoria}")])
    return InlineKeyboardMarkup(botones)

# Función para generar botones de tránsito

def generar_botones_transito(respuestas_legales):
    botones = []
    for clave in respuestas_legales:
        nombre = clave.replace("_", " ").capitalize()
        botones.append([InlineKeyboardButton(nombre, callback_data=f"transito:{clave}")])
    return InlineKeyboardMarkup(botones)

# Función para genenrar botones de documentos

def generar_botones_documentos(respuestas_legales):
    claves_documentos = [
        "placa", "revision", "seguro", "permiso", "homologacion"
    ]
    botones = []
    for clave in claves_documentos:
        nombre = clave.replace("_", " ").capitalize()
        botones.append([InlineKeyboardButton(nombre, callback_data=f"transito:{clave}")])
    return InlineKeyboardMarkup(botones)

# 📂 Categorías de infracciones de tránsito

categorias_legales_transito = {

    "📄 Documentación": [
        "placa", "revision", "seguro", "permiso", "homologacion", "licencia"
    ],

    "🅿️ Estacionamiento": [
    "acera", "pasopeatonal", "platabanda", "bandejon",
    "ciclovia", "grifo", "esquina", "porton", "prohibido",
    "cruce", "abandono", "discapacitados","paradalocomocion", "senales", "recintosmilitares"
    ],

    "🧰 Equipamiento obligatorio": [
        "vidrios_polarizados", "extintor", "grabado_patente" 
    ],
    "↩️ Maniobras": [
        "contra_sentido", "viraru", "viraje_indebido"
    ],
    
    "🚫 Vías exclusivas": [
        "vias_exclusivas"
    ],
    "🛑 Señales de tránsito": [
        "pare_no_detenerse", "ceda_el_paso", "luz_roja"
    ],
    "🧷 Usos obligatorios": [
        "cinturon_seguridad", "lentes"
],
   
}

# Handler principal

async def manejar_botones(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    opcion = query.data

    # ▶️ Menú principal
    if opcion == "ver_leyes":
        await leyes(update, context)

    elif opcion == "ver_comandos":
        await query.message.reply_text("📦 Escribe /ayuda o /tema para ver los comandos disponibles.")

    elif opcion == "ver_estado":
        await estado(update, context)

    elif opcion == "ver_cuadrantes":
        await mostrar_cuadrantes(update, context)

    # 🚦 Mostrar categorías de tránsito
    elif opcion == "ver_transito":
        markup = generar_botones_categorias_transito(categorias_legales_transito)
        await query.message.reply_text(
            "🚦 *Categorías de infracciones de tránsito*\nSelecciona una categoría para ver sus infracciones:",
            reply_markup=markup,
            parse_mode=ParseMode.MARKDOWN
        )

    # 🚦 Mostrar infracciones dentro de una categoría
    elif opcion.startswith("categoria:"):
        categoria = opcion.split("categoria:")[1]
        claves = categorias_legales_transito.get(categoria)

        if claves:
            botones = []
            for clave in claves:
                nombre = clave.replace("_", " ").capitalize()
                botones.append([InlineKeyboardButton(nombre, callback_data=f"transito:{clave}")])

            teclado = InlineKeyboardMarkup(botones)
            await query.message.reply_text(
                f"🚦 *Infracciones en:* `{categoria.replace('_', ' ').capitalize()}`",
                reply_markup=teclado,
                parse_mode=ParseMode.MARKDOWN
            )
        else:
            await query.message.reply_text("⚠️ No se encontraron infracciones para esa categoría.")

    # 🚦 Mostrar definición de una infracción
    elif opcion.startswith("transito:"):
        clave = opcion.split("transito:")[1]
        respuesta = respuestas_legales.get(clave)

        if respuesta:
            boton_volver = InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Volver al menú de tránsito", callback_data="ver_transito")]
            ])
            await query.message.reply_text(respuesta, reply_markup=boton_volver, parse_mode=ParseMode.MARKDOWN)
        else:
            await query.message.reply_text("⚠️ No se encontró información para esa infracción.")

    # 📘 Definiciones por comando
    elif opcion.startswith("def:"):
        termino = opcion.split("def:")[1]
        definicion = definiciones.get(termino)

        if definicion:
            mensaje = f"📌 *{termino.replace('_', ' ').capitalize()}*\n{definicion}"
            boton_volver = InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Volver al menú", callback_data="ver_comandos")]
            ])
            await query.message.reply_text(mensaje, reply_markup=boton_volver, parse_mode=ParseMode.MARKDOWN)
        else:
            await query.message.reply_text("⚠️ No se encontró esa definición.")

    # 📂 Comandos por tema
    elif opcion.startswith("tema:"):
        tema = opcion.split("tema:")[1]
        comandos = categorias.get(tema)

        if comandos:
            botones = []
            for cmd in comandos:
                nombre = cmd.replace("_", " ").capitalize()
                botones.append([InlineKeyboardButton(nombre, callback_data=f"def:{cmd}")])

            teclado = InlineKeyboardMarkup(botones)
            await query.message.reply_text(
                f"📘 *Comandos relacionados con:* `{tema}`",
                reply_markup=teclado,
                parse_mode=ParseMode.MARKDOWN
            )
        else:
            await query.message.reply_text("❌ No se encontró ese tema.")

    # 📞 Cuadrantes
    elif opcion.startswith("cuad:"):
        codigo = opcion.split("cuad:")[1]
        numero = cuadrantes.get(codigo)

        if numero:
            mensaje = f"📞 *Cuadrante {codigo}*\nNúmero de contacto: `{numero}`"
            await query.message.reply_text(mensaje, parse_mode=ParseMode.MARKDOWN)
        else:
            await query.message.reply_text("❌ No se encontró ese cuadrante.")

    # ❓ Opción no reconocida
    else:
        logging.warning(f"Opción no reconocida: {opcion}")
        await query.message.reply_text("❓ Opción no reconocida.")

#HEADLER COMANDO MENU

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if update.message.chat.type not in ["group", "supergroup"]:
            return

        teclado = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("📘 Leyes", callback_data="ver_leyes"),
                InlineKeyboardButton("📗 Ordenanzas", callback_data="ver_ordenanzas"),
            ],
            [
                InlineKeyboardButton("🚦 Tránsito", callback_data="ver_transito"),
                InlineKeyboardButton("🌱 Medioambiente", callback_data="tema:medioambiente")
            ],
            [
                InlineKeyboardButton("ℹ️ Estado", callback_data="ver_estado"),
                InlineKeyboardButton("🚓 Cuadrantes", callback_data="ver_cuadrantes"),
            ]
        ])

        mensaje = "🔧 *Menú Principal del Bot*\n\nElige una opción temática o funcional:"
        await update.message.reply_text(mensaje, reply_markup=teclado, parse_mode=ParseMode.MARKDOWN)

    except Exception as e:
        logging.error(f"Error en /menu: {e}")

#HEARDLER LEYES

async def leyes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        mensaje = "📚 *Acceso directo a las leyes referenciadas por el bot:*"
        teclado = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🚦 Ley de Tránsito", url="https://www.bcn.cl/leychile/navegar?idNorma=1007469"),
                InlineKeyboardButton("🍷 Ley de Alcoholes", url="https://www.bcn.cl/leychile/navegar?idNorma=220208"),
            ],
            [
                InlineKeyboardButton("🏦 Ley de rentas", url="https://www.bcn.cl/leychile/navegar?idNorma=1214890"),
                InlineKeyboardButton("🐶 Ley Cholito", url="https://www.bcn.cl/leychile/navegar?idNorma=1106037"),
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

#HEADLER ORDENANZAS   
     
async def ordenanzas(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        mensaje = "📗 *Ordenanzas municipales relevantes:*"
        teclado = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🌱 Ordenanza 37 Medioambiente", url="https://www.bcn.cl/leychile/navegar?idNorma=1209493"),
                InlineKeyboardButton("🛒 Ordenanza 38 Ferias libres", url="https://bcn.cl/pnHkl6"),
            ],
            [ 
                InlineKeyboardButton("🏗️ Ordenanza Edificación y urbanismo", url="https://www.bcn.cl/leychile/navegar?idNorma=1093294&idVersion=2025-07-25&idParte="),
            ]
        ])
        target = update.callback_query.message if update.callback_query else update.message
        await target.reply_text(mensaje, reply_markup=teclado, parse_mode=ParseMode.MARKDOWN)
    except Exception as e:
        logging.error(f"Error en /ordenanzas: {e}")

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

#HEADLER TEMA

async def mostrar_tema(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if not context.args:
            await update.message.reply_text(
                "🧭 Escribe el nombre de un tema. Ejemplo:\n`/tema transito` o `/tema medioambiente`",
                parse_mode=ParseMode.MARKDOWN
            )
            return

        tema = " ".join(context.args).lower()

        if tema not in categorias:
            await update.message.reply_text(
                f"❌ No se encontró el tema: `{tema}`",
                parse_mode=ParseMode.MARKDOWN
            )
            return

        botones = []
        for cmd in categorias[tema]:
            nombre = cmd.replace("_", " ").capitalize()
            botones.append([InlineKeyboardButton(nombre, callback_data=f"cat:{cmd}")])

        teclado = InlineKeyboardMarkup(botones)
        await update.message.reply_text(
            f"📘 *Categorías disponibles en:* `{tema}`",
            reply_markup=teclado,
            parse_mode=ParseMode.MARKDOWN
        )

    except Exception as e:
        logging.error(f"Error en /tema: {e}")
        await update.message.reply_text("❌ Hubo un error al mostrar el tema.")

#HEADLER CUADRANTES
async def mostrar_cuadrantes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    botones = []
    for codigo in cuadrantes.keys():
        botones.append([InlineKeyboardButton(codigo, callback_data=f"cuad:{codigo}")])

    teclado = InlineKeyboardMarkup(botones)

    target = update.callback_query.message if update.callback_query else update.message
    await target.reply_text(
        "🚓 *Selecciona un cuadrante para ver su número de contacto:*",
        reply_markup=teclado,
        parse_mode=ParseMode.MARKDOWN
    )

#HERADLER COMANDO ESTACIONAR

terminos_estacionar = [
    'acera', 'pasopeatonal', 'platabanda', 'bandejon', 'areaverde',
    'ciclovia', 'grifo', 'esquina', 'porton', 'prohibido',
    'cruce', 'abandono'
]

async def estacionar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    botones = []
    for termino in terminos_estacionar:
        nombre = termino.replace("_", " ").capitalize()
        botones.append([InlineKeyboardButton(nombre, callback_data=f"def:{termino}")])

    teclado = InlineKeyboardMarkup(botones)

    await update.message.reply_text(
        "🚗 *Normas sobre estacionamiento:*\nSelecciona una infracción para ver su detalle:",
        reply_markup=teclado,
        parse_mode=ParseMode.MARKDOWN
    )

#HEADLER COMANDO DOCUMENTOS

async def mostrar_documentos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    botones = []
    claves_documentos = [
        "placa", "revision", "seguro", "permiso", "homologacion"
    ]
    for clave in claves_documentos:
        nombre = clave.replace("_", " ").capitalize()
        botones.append([InlineKeyboardButton(nombre, callback_data=f"transito:{clave}")])

    teclado = InlineKeyboardMarkup(botones)
    await update.message.reply_text(
        "📄 *Documentación obligatoria para conducir*\nSelecciona un ítem para ver el detalle:",
        reply_markup=teclado,
        parse_mode=ParseMode.MARKDOWN
    )

# --- Registrar handlers de comandos ---
application.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, bienvenida_nuevo_miembro))
application.add_handler(CommandHandler("id", obtener_id))
application.add_handler(CommandHandler("ayuda", ayuda))
application.add_handler(CommandHandler("estado", estado))
application.add_handler(CommandHandler("debug", debug))
application.add_handler(CommandHandler("version", version))
application.add_handler(CommandHandler("menu", menu))
application.add_handler(CommandHandler("anunciar_prueba", anunciar_prueba))
application.add_handler(CommandHandler("prueba", avisar_prueba_comandos))
application.add_handler(CommandHandler("leyes", leyes))
application.add_handler(CommandHandler("buscar", buscar_definicion))
application.add_handler(CommandHandler("tema", mostrar_tema))
application.add_handler(CommandHandler("cuadrantes", mostrar_cuadrantes))
application.add_handler(CommandHandler("estacionar", estacionar))
application.add_handler(CommandHandler("documentos", mostrar_documentos))

# --- Registrar handlers de botones específicos ---
application.add_handler(CallbackQueryHandler(ordenanzas, pattern="^ver_ordenanzas$"))

# --- Registrar handler de botones genérico ---
application.add_handler(CallbackQueryHandler(manejar_botones))

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



# --- Ejecución por consola ---

if __name__ == "__main__":
    print("🚀 Iniciando bot...", flush=True)
    asyncio.run(application.run_polling())