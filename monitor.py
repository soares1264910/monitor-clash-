import os
import time
import requests
from datetime import datetime, timezone, timedelta

PLAYER_TAG = "#QRG8YPJU"

POLL_INTERVAL_SECONDS = 10
RUN_TIME_SECONDS = 290

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
        print(f"Erro na API: {e}")
        return None


def parse_battle_time(battle_time):
    for fmt in (
        "%Y%m%dT%H%M%S.%fZ",
        "%Y%m%dT%H%M%SZ"
    ):
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
    url = (
        f"https://api.telegram.org/"
        f"bot{TELEGRAM_TOKEN}/sendMessage"
    )

    response = requests.post(
        url,
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
        return False

    battle_datetime = parse_battle_time(battle_time)

    if not battle_datetime:
        print(f"Formato desconhecido: {battle_time}")
        return False

    now = datetime.now(timezone.utc)

    seconds_ago = (
        now - battle_datetime
    ).total_seconds()

    print(
        f"Última batalha: {battle_time} | "
        f"idade: {seconds_ago:.0f}s"
    )

    if seconds_ago < 0 or seconds_ago > 600:
        print("Batalha não é recente.")
        return False

    battle_id = battle_time

    last_notified = get_last_notified()

    if battle_id == last_notified:
        print("Já notificada.")
        return False

    brasilia_time = (
        battle_datetime - timedelta(hours=3)
    )

    inicio = brasilia_time.strftime("%H:%M:%S")
    detectada = datetime.now().strftime("%H:%M:%S")

    atraso = max(0, int(seconds_ago))

    message = (
        "🚨 BATALHA DETECTADA! 🚨\n\n"
        "👤 O jogador iniciou uma batalha.\n"
        f"🕐 Início registrado: {inicio}\n"
        f"📡 Detectada: {detectada}\n"
        f"⏱️ Diferença registrada: {atraso}s\n\n"
        "👀 ENTRA NO CLASH AGORA!"
    )

    send_telegram(message)

    save_last_notified(battle_id)

    print("NOVA BATALHA!")
    print(f"Início: {inicio}")
    print(f"Detectada: {detectada}")
    print(f"Atraso observado: {atraso}s")
    print("Telegram enviado!")

    return True


print("CLASH MONITOR INICIADO")

start_time = time.time()

while True:

    elapsed = time.time() - start_time

    if elapsed >= RUN_TIME_SECONDS:
        print("Tempo de monitoramento encerrado.")
        break

    print()
    print(
        f"Consultando API: "
        f"{datetime.now().strftime('%H:%M:%S')}"
    )

    if check_battle():
        break

    elapsed = time.time() - start_time
    remaining = RUN_TIME_SECONDS - elapsed

    if remaining <= 0:
        break

    time.sleep(
        min(POLL_INTERVAL_SECONDS, remaining)
    )

print("Monitor finalizado.")
