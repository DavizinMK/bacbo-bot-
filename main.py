from fastapi import FastAPI
from telegram import Bot
import os

app = FastAPI()

TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

bot = Bot(token=TOKEN)

estado = "IDLE"
lado = None
tentativa = 0
score_minimo = 9

def calcular_score(dados):
    score = 0

    if dados["big_road"] == "favoravel":
        score += 3
    if dados["derivados"] == "estaveis":
        score += 3
    if dados["numeros"] == "neutros":
        score += 1
    if dados["percentual"] == "dominante":
        score += 2

    return score

@app.post("/dados")
async def receber_dados(dados: dict):
    global estado, lado, tentativa

    score = calcular_score(dados)

    if estado == "IDLE" and score >= score_minimo:
        estado = "ALERTA"
        lado = dados["ultimo_resultado"]

        await bot.send_message(
            chat_id=CHAT_ID,
            text="🔔 Possível entrada detectada.\nAguardando confirmação."
        )

    elif estado == "ALERTA":
        if dados["ultimo_resultado"] == lado:
            estado = "ENTRADA"
            tentativa = 1

            await bot.send_message(
                chat_id=CHAT_ID,
                text=f"✅ SINAL CONFIRMADO\n\n➡️ Entrada: {lado}\n🛡 Proteção: empate (G1)"
            )
        elif score < score_minimo:
            estado = "IDLE"

    elif estado == "ENTRADA":
        if dados["ultimo_resultado"] == lado:
            await bot.send_message(chat_id=CHAT_ID, text="🟢 GREEN")
            estado = "IDLE"
        else:
            if tentativa == 1:
                tentativa += 1
                await bot.send_message(chat_id=CHAT_ID, text="⚠️ Proteção G1\nMantendo entrada.")
            else:
                await bot.send_message(chat_id=CHAT_ID, text="🔴 RED\nEncerrado (G1).")
                estado = "IDLE"

    return {"status": estado}
