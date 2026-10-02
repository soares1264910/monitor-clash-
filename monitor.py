import os
import time
import requests

print("🚀 CLASH MONITOR INICIADO")

# =========================
# CONFIGURAÇÕES
# =========================

PLAYER_TAG = "#QRG8YPJU"

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

API_URL = (
    "https://proxy.royaleapi.dev/v1/players/"
    + requests.utils.quote(PLAYER_TAG, safe="")
    + "/battlelog"
)

LAST_BATTLE_FILE = "last_battle.txt"

# Tempo que o monitor fica rodando em cada execução
RUN_TIME = 290

# Intervalo entre consultas
CHECK_INTERVAL = 10


# =========================
# TELEGRAM
# =========================

def enviar_telegram(mensagem):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("ERRO: variáveis do Telegram não configuradas.")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": mensagem
    }

    try:
        resposta = requests.post(url, data=data, timeout=15)

        if resposta.ok:
            print("Mensagem enviada para o Telegram.")
        else:
            print("Erro ao enviar Telegram:")
            print(resposta.text)

    except Exception as e:
        print("Erro no Telegram:", e)


# =========================
# ÚLTIMA BATALHA REGISTRADA
# =========================

def carregar_ultima_batalha():
    if not os.path.exists(LAST_BATTLE_FILE):
        return None

    try:
        with open(LAST_BATTLE_FILE, "r", encoding="utf-8") as arquivo:
            return arquivo.read().strip()
    except Exception:
        return None


def salvar_ultima_batalha(battle_id):
    with open(LAST_BATTLE_FILE, "w", encoding="utf-8") as arquivo:
        arquivo.write(str(battle_id))


# =========================
# BUSCAR BATTLELOG
# =========================

def buscar_batalhas():
    try:
        resposta = requests.get(API_URL, timeout=20)

        print("Status da API:", resposta.status_code)

        if resposta.status_code != 200:
            print("Erro na API:")
            print(resposta.text)
            return []

        return resposta.json()

    except Exception as e:
        print("Erro ao consultar Battlelog:", e)
        return []


# =========================
# IDENTIFICAR BATALHA
# =========================

def identificar_batalha(batalha):
    try:
        jogador = batalha.get("team", [{}])[0]

        jogador_tag = jogador.get("tag")

        if jogador_tag != PLAYER_TAG:
            return None

        timestamp = batalha.get("battleTime")

        if timestamp:
            return timestamp

    except Exception as e:
        print("Erro ao identificar batalha:", e)

    return None


# =========================
# MONITOR
# =========================

def monitorar():

    print("Monitorando jogador:", PLAYER_TAG)

    ultima_batalha = carregar_ultima_batalha()

    if ultima_batalha:
        print("Última batalha registrada:", ultima_batalha)
    else:
        print("Nenhuma batalha registrada anteriormente.")

    inicio = time.time()

    while time.time() - inicio < RUN_TIME:

        print("Consultando Battlelog...")

        batalhas = buscar_batalhas()

        if batalhas:

            print("Batalhas encontradas:", len(batalhas))

            batalha_atual = None

            for batalha in batalhas:

                battle_id = identificar_batalha(batalha)

                if battle_id:
                    batalha_atual = battle_id
                    break

            if batalha_atual:

                print("Batalha mais recente:", batalha_atual)

                if ultima_batalha is None:

                    salvar_ultima_batalha(batalha_atual)

                    ultima_batalha = batalha_atual

                    print("Primeira batalha registrada. Não enviando alerta.")

                elif batalha_atual != ultima_batalha:

                    print("NOVA BATALHA DETECTADA!")

                    mensagem = (
                        "🚨 NOVA BATALHA DETECTADA!\n\n"
                        "O jogador começou uma nova batalha no Clash Royale."
                    )

                    enviar_telegram(mensagem)

                    salvar_ultima_batalha(batalha_atual)

                    ultima_batalha = batalha_atual

        else:
            print("Nenhuma batalha encontrada.")

        time.sleep(CHECK_INTERVAL)

    print("Monitor finalizado.")


# =========================
# INICIAR
# =========================

if __name__ == "__main__":
    monitorar()
