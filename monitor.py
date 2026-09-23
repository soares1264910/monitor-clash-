import os
import requests
from datetime import datetime, timezone

PLAYER_TAG = "#QRG8YPJU"

CR_API_KEY = os.environ["CR_API_KEY"]
TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

# Consulta o histórico de batalhas
url = f"https://proxy.royaleapi.dev/v1/players/{requests.utils.quote(PLAYER_TAG, safe='')}/battlelog"

headers = {
    "Authorization": f"Bearer {CR_API_KEY}"
}

response = requests.get(url, headers=headers, timeout=20)
response.raise_for_status()

battles = response.json()

if not battles:
    raise SystemExit

latest_battle = battles[0]

# Pega o horário da última batalha
battle_time = latest_battle.get("battleTime")

if not battle_time:
    raise SystemExit

# Converte o horário da API para datetime
battle_datetime = datetime.strptime(
    battle_time,
    "%Y%m%dT%H%M%S.%fZ"
).replace(tzinfo=timezone.utc)

now = datetime.now(timezone.utc)

# Calcula há quantos segundos aconteceu
seconds_ago = (now - battle_datetime).total_seconds()

# Só considera batalha realmente recente
if seconds_ago < 0 or seconds_ago > 120:
    raise SystemExit

# Identifica a batalha para não mandar a mesma notificação duas vezes
battle_id = battle_time

state_file = "last_battle.txt"

try:
    with open(state_file, "r") as f:
        last_battle = f.read().strip()
except FileNotFoundError:
    last_battle = ""

if battle_id == last_battle:
    raise SystemExit

# Envia a notificação
message = "🚨 O jogador entrou em uma batalha no Clash Royale! 👀"

telegram_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

requests.post(
    telegram_url,
    data={
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message
    },
    timeout=20
).raise_for_status()

# Salva a batalha já notificada
with open(state_file, "w") as f:
    f.write(battle_id)