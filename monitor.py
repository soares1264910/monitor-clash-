import os
import requests

PLAYER_TAG = "#QRG8YPJU"
CR_API_KEY = os.environ["CR_API_KEY"]
TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

url = f"https://api.clashroyale.com/v1/players/{requests.utils.quote(PLAYER_TAG, safe='')}/battlelog"

headers = {
    "Authorization": f"Bearer {CR_API_KEY}"
}

response = requests.get(url, headers=headers, timeout=20)
response.raise_for_status()

battles = response.json()

if not battles:
    raise SystemExit

latest_battle = battles[0]

battle_id = (
    latest_battle.get("battleTime")
    or str(latest_battle)
)

state_file = "last_battle.txt"

try:
    with open(state_file, "r") as f:
        last_battle = f.read().strip()
except FileNotFoundError:
    last_battle = ""

if battle_id != last_battle:
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

    with open(state_file, "w") as f:
        f.write(battle_id)
