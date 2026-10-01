import os
import requests
from datetime import datetime, timezone, timedelta

PLAYER_TAG = "#QRG8YPJU"

# Considera batalhas dos últimos 10 minutos.
MAX_BATTLE_AGE_SECONDS = 600

CR_API_KEY = os.environ["CR_API_KEY"]
TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

# ============================================================
# 1. CONSULTAR HISTÓRICO DE BATALHAS
# ============================================================

url = (
    "https://proxy.royaleapi.dev/v1/players/"
    f"{requests.utils.quote(PLAYER_TAG, safe='')}/battlelog"
)

headers = {
    "Authorization": f"Bearer {CR_API_KEY}"
}

response = requests.get(
    url,
    headers=headers,
    timeout=20
)

response.raise_for_status()

battles = response.json()

if not battles:
    print("Nenhuma batalha encontrada.")
    raise SystemExit(0)

# ============================================================
# 2. PEGAR A BATALHA MAIS RECENTE
# ============================================================

latest_battle = battles[0]

battle_time = latest_battle.get("battleTime")

if not battle_time:
    print("A batalha mais recente não possui battleTime.")
    raise SystemExit(0)

print(f"Batalha encontrada: {battle_time}")

# ============================================================
# 3. CONVERTER HORÁRIO DA BATALHA
# ============================================================

try:
    battle_datetime = datetime.strptime(
        battle_time,
        "%Y%m%dT%H%M%S.%fZ"
    ).replace(tzinfo=timezone.utc)

except ValueError:

    try:
        battle_datetime = datetime.strptime(
            battle_time,
            "%Y%m%dT%H%M%SZ"
        ).replace(tzinfo=timezone.utc)

    except ValueError:
        print(f"Formato de battleTime não reconhecido: {battle_time}")
        raise SystemExit(0)

# ============================================================
# 4. VERIFICAR QUANTO TEMPO PASSOU
# ============================================================

now = datetime.now(timezone.utc)

seconds_ago = (now - battle_datetime).total_seconds()

print(
    f"A batalha aconteceu há aproximadamente "
    f"{seconds_ago:.0f} segundos."
)

if seconds_ago < 0:
    print("A batalha possui horário futuro. Ignorando.")
    raise SystemExit(0)

if seconds_ago > MAX_BATTLE_AGE_SECONDS:
    print("A última batalha não é recente. Nada a fazer.")
    raise SystemExit(0)

# ============================================================
# 5. VERIFICAR SE JÁ FOI NOTIFICADA
# ============================================================

battle_id = battle_time
state_file = "last_battle.txt"

try:
    with open(state_file, "r", encoding="utf-8") as f:
        last_battle = f.read().strip()

except FileNotFoundError:
    last_battle = ""

if battle_id == last_battle:
    print("Essa batalha já foi notificada.")
    raise SystemExit(0)

# ============================================================
# 6. CONVERTER HORÁRIO PARA BRASÍLIA
# ============================================================

brasilia_time = battle_datetime - timedelta(hours=3)

horario = brasilia_time.strftime("%H:%M:%S")

# ============================================================
# 7. ENVIAR NOTIFICAÇÃO PARA O TELEGRAM
# ============================================================

message = (
    "🚨 BATALHA DETECTADA! 🚨\n\n"
    "👤 O jogador entrou em batalha!\n"
    f"🕐 Início: {horario}\n\n"
    "👀 ENTRA NO CLASH AGORA!"
)

telegram_url = (
    f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
)

telegram_response = requests.post(
    telegram_url,
    data={
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message
    },
    timeout=20
)

telegram_response.raise_for_status()

# ============================================================
# 8. SALVAR COMO NOTIFICADA
# ============================================================

with open(state_file, "w", encoding="utf-8") as f:
    f.write(battle_id)

print("✅ Notificação enviada para o Telegram!")
print(f"🕐 Horário da batalha: {horario}")
print(f"✅ Batalha salva como: {battle_id}")
