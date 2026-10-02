import os
import time
import requests
from datetime import datetime, timezone, timedelta

PLAYER_TAG = "#QRG8YPJU"

# Consulta a API a cada 15 segundos enquanto o monitor estiver ativo.
POLL_INTERVAL_SECONDS = 15

# O GitHub Actions executará o monitor por até 4 minutos.
RUN_TIME_SECONDS = 240

CR_API_KEY = os.environ["CR_API_KEY"]
TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

STATE_FILE = "last_battle.txt"

API_URL = (
    "https://proxy.royaleapi.dev/v1/players/"
    f"{requests.utils.quote(PLAYER_TAG, safe='')}/battlelog"
)

HEADERS = {
    "Authorization": f"Bearer {CR_API_KEY}"
}


def get_last_battle():
    try:
        response = requests.get(
            API_URL,
            headers=HEADERS,
            timeout=20
        )

        response.raise_for_status()

        battles = response.json()

        if not battles:
            print("Nenhuma batalha encontrada.")
            return None

        return battles[0]

    except requests.RequestException as e:
        print(f"Erro ao consultar a API: {e}")
        return None


def parse_battle_time(battle_time):
    formats = [
        "%Y%m%dT%H%M%S.%fZ",
        "%Y%m%dT%H%M%SZ"
    ]

    for fmt in formats:
        try:
            return datetime.strptime(
                battle_time,
                fmt
            ).replace(tzinfo=timezone.utc)
        except ValueError:
            pass

    return None


def get_last_notified():
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return f.read().strip()
    except FileNotFoundError:
        return ""


def save_last_notified(battle_id):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        f.write(battle_id)


def send_telegram(message):
    telegram_url = (
        f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    )

    response = requests.post(
        telegram_url,
        data={
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message
        },
        timeout=20
    )

    response.raise_for_status()


def check_battle():

    battle = get_last_battle()

    if not battle:
        return False

    battle_time = battle.get("battleTime")

    if not battle_time:
        print("A batalha não possui battleTime.")
        return False

    print(f"Batalha mais recente na API: {battle_time}")

    battle_datetime = parse_battle_time(battle_time)

    if not battle_datetime:
        print(
            f"Formato de battleTime não reconhecido: "
            f"{battle_time}"
        )
        return False

    now = datetime.now(timezone.utc)

    seconds_ago = (
        now - battle_datetime
    ).total_seconds()

    print(
        f"A batalha foi registrada há "
        f"{seconds_ago:.0f} segundos."
    )

    # Ignora horários futuros.
    if seconds_ago < 0:
        print("Batalha com horário futuro. Ignorando.")
        return False

    # Ignora batalhas muito antigas.
    if seconds_ago > 900:
        print("Batalha antiga. Ignorando.")
        return False

    battle_id = battle_time

    last_notified = get_last_notified()

    if battle_id == last_notified:
        print("Essa batalha já foi notificada.")
        return False

    # Converte UTC para horário de Brasília.
    brasilia_time = (
        battle_datetime - timedelta(hours=3)
    )

    horario = brasilia_time.strftime("%H:%M:%S")

    detected_at = datetime.now().strftime("%H:%M:%S")

    message = (
        "🚨 BATALHA DETECTADA! 🚨\n\n"
        "👤 O jogador entrou em batalha!\n"
        f"🕐 Início registrado: {horario}\n"
        f"📡 Detectada pelo monitor: {detected_at}\n\n"
        "👀 ENTRA NO CLASH AGORA!"
    )

    print("📨 Enviando notificação para o Telegram...")

    send_telegram(message)

    save_last_notified(battle_id)

    print("✅ Notificação enviada!")
    print(f"🕐 Horário da batalha: {horario}")
    print(f"📡 Detectada às: {detected_at}")
    print(f"🆔 Batalha: {battle_id}")

    return True


print("=" * 60)
print("🚀 CLASH MONITOR INICIADO")
print("=" * 60)

start_time = time.time()

while True:

    elapsed = time.time() - start_time

    if elapsed >= RUN_TIME_SECONDS:
        print("⏹️ Tempo de monitoramento encerrado.")
        break

    print()
    print(
        f"🔎 Consultando API... "
        f"{datetime.now().strftime('%H:%M:%S')}"
    )

    detected = check_battle()

    if detected:
        print("🎯 Nova batalha detectada!")
        break

    elapsed = time.time() - start_time
    remaining = RUN_TIME_SECONDS - elapsed

    if remaining <= 0:
        break

    sleep_time = min(
        POLL_INTERVAL_SECONDS,
        remaining
    )

    print(
        f"😴 Aguardando {sleep_time:.0f} segundos..."
    )

    time.sleep(sleep_time)

print()
print("✅ Monitor finalizado.")
