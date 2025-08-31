from domains.barbearia import barbearia
from core.chatbot import Chatbot

bot = Chatbot(barbearia)

print("ChatBot da Barbearia iniciado! Digite 'sair' para encerrar.\n")

while True:
    mensagem = input("Você: ")
    if mensagem.lower() == "sair":
        print("ChatBot: Até logo! 💈")
        break
    resposta = bot.processar(mensagem)
    print(f"ChatBot: {resposta}\n")
