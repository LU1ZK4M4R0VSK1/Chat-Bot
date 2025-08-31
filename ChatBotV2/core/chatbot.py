import re

class Chatbot:
    def __init__(self, empresa):
        self.empresa = empresa
        self.nome_empresa = empresa.get("nome", "Empresa")
        # Dicionário para armazenar o estado da conversa de cada usuário
        self.conversas = {}

    def _get_user_state(self, user_id):
        """Retorna o estado da conversa para um usuário, criando um se não existir."""
        if user_id not in self.conversas:
            self.conversas[user_id] = {
                'estado_conversa': None,
                'dados_agendamento': {}
            }
        return self.conversas[user_id]

    def _resetar_estado(self, user_id):
        """Reseta o estado da conversa para um usuário específico."""
        if user_id in self.conversas:
            self.conversas[user_id]['estado_conversa'] = None
            self.conversas[user_id]['dados_agendamento'] = {}

    def _detectar_intencoes(self, mensagem):
        intencoes = []
        mensagem_lower = mensagem.lower()
        
        for intencao, palavras in self.empresa["palavras_chave"].items():
            if any(palavra in mensagem_lower for palavra in palavras):
                intencoes.append(intencao)
        
        if 'agendamento' not in intencoes:
            if any(servico in mensagem_lower for servico in self.empresa["servicos"]):
                intencoes.append('agendamento')

        return intencoes

    def processar(self, user_id, mensagem):
        """Processa a mensagem de um usuário específico."""
        user_state = self._get_user_state(user_id)

        if user_state['estado_conversa']:
            return self._handle_estado_conversa(user_id, mensagem)

        intencoes = self._detectar_intencoes(mensagem)
        mensagem_lower = mensagem.lower()

        if not intencoes:
            return self.empresa["respostas"]["padrao"]

        resposta_final = []
        acao_principal_executada = False

        if 'saudacao' in intencoes:
            if "tudo bem" in mensagem_lower and "?" in mensagem_lower:
                resposta_final.append(self.empresa["respostas"]["resposta_tudo_bem"])
            else:
                resposta_final.append(self.empresa["respostas"]["saudacao"])

        if 'agendamento' in intencoes:
            resposta_final.append(self._iniciar_agendamento(user_id, mensagem))
            acao_principal_executada = True
        elif 'preco' in intencoes:
            resposta_final.append(self.empresa["respostas"]["precos"])
            acao_principal_executada = True
        elif 'horario_funcionamento' in intencoes:
            resposta_final.append(self.empresa["respostas"]["horario"])
            acao_principal_executada = True
        
        if 'despedida' in intencoes:
            resposta_final.append(self.empresa["respostas"]["despedida"])
            acao_principal_executada = True

        if not acao_principal_executada and 'saudacao' in intencoes:
            if "tudo bem" not in mensagem_lower:
                resposta_final.append(self.empresa["respostas"]["pergunta_tudo_bem"])
            resposta_final.append(self.empresa["respostas"]["boas_vindas"].format(nome_empresa=self.nome_empresa))

        return " ".join(resposta_final) if resposta_final else self.empresa["respostas"]["padrao"]

    def _handle_estado_conversa(self, user_id, mensagem):
        estado_atual = self._get_user_state(user_id)['estado_conversa']
        if estado_atual == 'agendando_servico':
            return self._handle_agendamento_servico(user_id, mensagem)
        if estado_atual == 'agendando_dia_hora':
            return self._handle_agendamento_dia_hora(user_id, mensagem)
        if estado_atual == 'aguardando_confirmacao_final':
            return self._handle_confirmacao_final(user_id, mensagem)
        return self.empresa["respostas"]["padrao"]

    def _iniciar_agendamento(self, user_id, mensagem):
        user_state = self._get_user_state(user_id)
        for servico in self.empresa["servicos"]:
            if servico in mensagem.lower():
                user_state['dados_agendamento']['servico'] = servico
                user_state['estado_conversa'] = 'agendando_dia_hora'
                return self.empresa["respostas"]["agendamento_pedir_data"].format(servico=servico)
        
        user_state['estado_conversa'] = 'agendando_servico'
        lista_servicos = ", ".join(self.empresa["servicos"])
        return self.empresa["respostas"]["agendamento_iniciar"].format(lista_servicos=lista_servicos)

    def _handle_agendamento_servico(self, user_id, mensagem):
        user_state = self._get_user_state(user_id)
        for servico in self.empresa["servicos"]:
            if servico in mensagem.lower():
                user_state['dados_agendamento']['servico'] = servico
                user_state['estado_conversa'] = 'agendando_dia_hora'
                return self.empresa["respostas"]["agendamento_pedir_data"].format(servico=servico)
        
        lista_servicos = ", ".join(self.empresa["servicos"])
        return self.empresa["respostas"]["agendamento_servico_invalido"].format(lista_servicos=lista_servicos)

    def _handle_agendamento_dia_hora(self, user_id, mensagem):
        user_state = self._get_user_state(user_id)
        match = re.search(r"(.*?) (?:às|as|de) (\d{1,2}(?::\d{2})?h?)", mensagem.lower())
        if match:
            dia = match.group(1).strip()
            hora = match.group(2).strip()
            servico = user_state['dados_agendamento'].get('servico', 'serviço')
            
            user_state['estado_conversa'] = 'aguardando_confirmacao_final'
            return self.empresa["respostas"]["agendamento_confirmar"].format(servico=servico, dia=dia, hora=hora)
        else:
            return self.empresa["respostas"]["agendamento_data_invalida"]

    def _handle_confirmacao_final(self, user_id, mensagem):
        intencoes = self._detectar_intencoes(mensagem)
        self._resetar_estado(user_id)

        if 'confirmacao_positiva' in intencoes:
            return self.empresa["respostas"]["confirmacao_final_positiva"]
        if 'confirmacao_negativa' in intencoes:
            return self.empresa["respostas"]["confirmacao_final_negativa"]
        
        return self.processar(user_id, mensagem)
