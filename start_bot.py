import time
import subprocess

print("🔁 Iniciando ciclo persistente del bot...")

while True:
    try:
        subprocess.run(["python3", "bot.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ El bot se cayó con error: {e}. Reiniciando en 10 segundos...")
        time.sleep(10)
    else:
        print("✅ El bot finalizó correctamente. Reiniciando en 10 segundos...")
        time.sleep(10)

