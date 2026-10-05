import os
import time
import requests
from urllib.parse import quote

print("🚀 CLASH MONITOR INICIADO")

PLAYER_TAG = "#QRG8YPJU"

CR_API_TOKEN = os.environ.get("CR_API_TOKEN")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

CHECK_INTERVAL = 5
RUN_TIME = 230

API_URL = (
    "https://proxy.royaleapi.dev/v1/players/"
    + quote(PLAYER_TAG, safe="")
    + "/battlelog"
)

STATE_FILE = "last_battle.txt"


def enviar_telegram(mensagem):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("❌ Telegram não configurado.")
        return False

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

    try:
        resposta = requests.post(
            url,
            data={
                "chat_id": TELEGRAM_CHAT_ID,
                "text": mensagem
            },
            timeout=15
        )

        if resposta.ok:
            print("✅ Mensagem enviada para o Telegram.")
            return True

        print("❌ Erro no Telegram:", resposta.text)

    except Exception as e:
        print("❌ Erro no Telegram:", e)

    return False


def carregar_ultima_batalha():
    if not os.path.exists(STATE_FILE):
        return None

    try:
        with open(STATE_FILE, "r", encoding="utf-8") as arquivo:
            return arquivo.read().strip()
    except Exception:
        return None


def salvar_ultima_batalha(battle_time):
    with open(STATE_FILE, "w", encoding="utf-8") as arquivo:
        arquivo.write(str(battle_time))


def buscar_batalhas():
    headers = {
        "Authorization": f"Bearer {CR_API_TOKEN}",
        "Accept": "application/json"
    }

    try:
        resposta = requests.get(
            API_URL,
            headers=headers,
            timeout=20
        )

        print("Status da API:", resposta.status_code)

        if resposta.status_code != 200:
            print("❌ Erro na API:", resposta.text)
            return []

        return resposta.json()

    except Exception as e:
        print("❌ Erro ao consultar Battlelog:", e)
        return []


def encontrar_batalha_do_jogador(batalhas):
    for batalha in batalhas:

        battle_time = batalha.get("battleTime")

        for jogador in batalha.get("team", []):

            if jogador.get("tag") == PLAYER_TAG:
                return battle_time

    return None


def monitorar():

    print("👀 Monitorando jogador:", PLAYER_TAG)
    print("⏱️ Intervalo:", CHECK_INTERVAL, "segundos")
    print("⏳ Duração deste ciclo:", RUN_TIME, "segundos")

    ultima_batalha = carregar_ultima_batalha()

    print("📌 Última batalha:", ultima_batalha)

    inicio = time.time()
    contador = 0

    while time.time() - inicio < RUN_TIME:

        contador += 1

        print()
        print(f"🔎 Consulta #{contador}")

        batalhas = buscar_batalhas()

        if batalhas:

            batalha_atual = encontrar_batalha_do_jogador(batalhas)

            print("⚔️ Batalha mais recente:", batalha_atual)

            if batalha_atual and batalha_atual != ultima_batalha:

                print("🚨 NOVA BATALHA DETECTADA!")

                mensagem = (
                    "🚨 NOVA BATALHA DETECTADA!\n\n"
                    "O jogador começou uma nova batalha no Clash Royale."
                )

                if enviar_telegram(mensagem):
                    salvar_ultima_batalha(batalha_atual)
                    ultima_batalha = batalha_atual

            else:
                print("😴 Nenhuma batalha nova.")

        time.sleep(CHECK_INTERVAL)

    print()
    print("🏁 CICLO FINALIZADO.")
    print("✅ Monitor encerrado normalmente.")


if __name__ == "__main__":
    monitorar()
