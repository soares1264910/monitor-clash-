import os
import time
import requests
from urllib.parse import quote

print("🚀 CLASH MONITOR INICIADO")

PLAYER_TAG = "#QRG8YPJU"

CR_API_TOKEN = os.environ.get("CR_API_TOKEN")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

# Verifica a API a cada 5 segundos
CHECK_INTERVAL = 5

# Tempo máximo de execução do GitHub Actions
RUN_TIME = 330 * 60

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

    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": mensagem
    }

    try:
        resposta = requests.post(
            url,
            data=data,
            timeout=15
        )

        if resposta.ok:
            print("✅ Mensagem enviada para o Telegram.")
            return True

        print("❌ Erro no Telegram:")
        print(resposta.text)

    except Exception as e:
        print("❌ Erro ao enviar Telegram:", e)

    return False


def carregar_ultima_batalha():
    if not os.path.exists(STATE_FILE):
        return None

    try:
        with open(STATE_FILE, "r", encoding="utf-8") as arquivo:
            return arquivo.read().strip()

    except Exception as e:
        print("❌ Erro ao ler estado:", e)
        return None


def salvar_ultima_batalha(battle_time):
    try:
        with open(STATE_FILE, "w", encoding="utf-8") as arquivo:
            arquivo.write(str(battle_time))

        print("💾 Última batalha salva:", battle_time)

    except Exception as e:
        print("❌ Erro ao salvar batalha:", e)


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
            print("❌ Erro na API:")
            print(resposta.text)
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

    ultima_batalha = carregar_ultima_batalha()

    if ultima_batalha:
        print("📌 Última batalha registrada:", ultima_batalha)
    else:
        print("📌 Nenhuma batalha registrada anteriormente.")

    inicio = time.time()
    consultas = 0

    while time.time() - inicio < RUN_TIME:

        consultas += 1

        print()
        print("=" * 50)
        print(f"🔎 Consulta #{consultas}")
        print("=" * 50)

        batalhas = buscar_batalhas()

        if batalhas:

            print("📋 Batalhas encontradas:", len(batalhas))

            batalha_atual = encontrar_batalha_do_jogador(batalhas)

            if batalha_atual:

                print("⚔️ Batalha mais recente:", batalha_atual)

                if ultima_batalha is None:

                    salvar_ultima_batalha(batalha_atual)
                    ultima_batalha = batalha_atual

                    print("📌 Primeira batalha registrada.")
                    print("🔕 Nenhuma mensagem enviada.")

                elif batalha_atual != ultima_batalha:

                    print()
                    print("🚨🚨🚨 NOVA BATALHA DETECTADA! 🚨🚨🚨")

                    mensagem = (
                        "🚨 NOVA BATALHA DETECTADA!\n\n"
                        "O jogador começou uma nova batalha no Clash Royale."
                    )

                    if enviar_telegram(mensagem):

                        salvar_ultima_batalha(batalha_atual)
                        ultima_batalha = batalha_atual

                    else:
                        print("⚠️ Mensagem não enviada. Tentaremos novamente.")

                else:

                    print("😴 Nenhuma batalha nova.")

        else:
            print("⚠️ Nenhuma batalha retornada pela API.")

        time.sleep(CHECK_INTERVAL)

    print()
    print("🏁 Tempo de execução terminado.")
    print("🔄 O próximo ciclo poderá iniciar pelo GitHub Actions.")


if __name__ == "__main__":
    monitorar()
