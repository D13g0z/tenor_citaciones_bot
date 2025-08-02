# ayuda

from respuestas import respuestas_legales
from respuestas_medioambiente import respuestas_medioambiente

def generar_mensaje_ayuda():
    mensaje = "📘 *Comandos:*\n\n"

    mensaje += "🚗 *Transito:*\n"
    for cmd in respuestas_legales:
        mensaje += f"• `/{cmd}`\n"

    mensaje += "\n🌱 *medioambiente:*\n"
    for cmd in respuestas_medioambiente:
        mensaje += f"• `/{cmd}`\n"

    mensaje += "\nℹ️ Escribe cualquiera de estos comandos para obtener la normativa correspondiente."
    return mensaje