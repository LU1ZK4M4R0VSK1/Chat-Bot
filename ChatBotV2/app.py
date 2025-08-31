from flask import Flask, request, jsonify
from domains.barbearia import barbearia
from core.chatbot import Chatbot

# Inicializa o aplicativo Flask
app = Flask(__name__)

# Instancia o chatbot (agora ele vai gerenciar múltiplos usuários)
bot = Chatbot(barbearia)

@app.route('/webhook', methods=['POST'])
def webhook():
    """Esta é a rota que recebe as mensagens do WhatsApp."""
    # Extrai os dados da mensagem do corpo da requisição (o formato pode variar com o provedor)
    # Exemplo de corpo esperado: { "user_id": "+5511999999999", "message": "Olá, tudo bem?" }
    data = request.get_json()

    if not data or 'user_id' not in data or 'message' not in data:
        return jsonify({"error": "Invalid request format"}), 400

    user_id = data['user_id']
    message = data['message']

    # Processa a mensagem usando o ID do usuário para manter o contexto
    response = bot.processar(user_id, message)

    # Retorna a resposta do bot em formato JSON
    return jsonify({"user_id": user_id, "response": response})

if __name__ == '__main__':
    # Roda o servidor de desenvolvimento do Flask
    app.run(debug=True)
