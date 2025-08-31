import re

class Chatbot:
    def __init__(self, empresa):
        self.empresa = empresa
        self.nome_empresa = empresa.get("nome", "Empresa")
        self.estado_conversa = None
        self.dados_agendamento = {}

    def _detectar_intencoes(self, mensagem):
        intencoes = []
        mensagem_lower = mensagem.lower()
        
        for intencao, palavras in self.empresa["palavras_chave"].items():
            if any(palavra in mensagem_lower for palavra in palavras):
                intencoes.append(intencao)
        
        # Lógica especial para serviços
        if 'agendamento' not in intencoes:
            if any(servico in mensagem_lower for servico in self.empresa["servicos"]):
                intencoes.append('agendamento')

        return intencoes

    def processar(self, mensagem):
        # 1. Processar com base no estado atual da conversa (máxima prioridade)
        if self.estado_conversa:
            return self._handle_estado_conversa(mensagem)

        # 2. Se não há estado, detectar intenções na mensagem
        intencoes = self._detectar_intencoes(mensagem)
        mensagem_lower = mensagem.lower()

        if not intencoes:
            return self.empresa["respostas"]["padrao"]

        # 3. Orquestrar respostas com base nas intenções
        resposta_final = []
        acao_principal_executada = False

        # Lógica de Saudação Aprimorada
        if 'saudacao' in intencoes:
            if "tudo bem" in mensagem_lower and "?" in mensagem_lower:
                resposta_final.append(self.empresa["respostas"]["resposta_tudo_bem"])
            else:
                resposta_final.append(self.empresa["respostas"]["saudacao"])

        # Prioridade para ações (agendamento, preço, etc.)
        if 'agendamento' in intencoes:
            resposta_final.append(self._iniciar_agendamento(mensagem))
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

        # Se não houve ação principal mas houve saudação, dar boas-vindas
        if not acao_principal_executada and 'saudacao' in intencoes:
            # Evita perguntar "Tudo bem?" se o usuário já falou
            if "tudo bem" not in mensagem_lower:
                resposta_final.append(self.empresa["respostas"]["pergunta_tudo_bem"])
            resposta_final.append(self.empresa["respostas"]["boas_vindas"].format(nome_empresa=self.nome_empresa))

        return " ".join(resposta_final) if resposta_final else self.empresa["respostas"]["padrao"]

    def _handle_estado_conversa(self, mensagem):
        estado_atual = self.estado_conversa
        if estado_atual == 'agendando_servico':
            return self._handle_agendamento_servico(mensagem)
        if estado_atual == 'agendando_dia_hora':
            return self._handle_agendamento_dia_hora(mensagem)
        if estado_atual == 'aguardando_confirmacao_final':
            return self._handle_confirmacao_final(mensagem)
        return self.empresa["respostas"]["padrao"]

    def _resetar_estado(self):
        self.estado_conversa = None
        self.dados_agendamento = {}

    def _iniciar_agendamento(self, mensagem):
        for servico in self.empresa["servicos"]:
            if servico in mensagem.lower():
                self.dados_agendamento['servico'] = servico
                self.estado_conversa = 'agendando_dia_hora'
                return self.empresa["respostas"]["agendamento_pedir_data"].format(servico=servico)
        
        self.estado_conversa = 'agendando_servico'
        lista_servicos = ", ".join(self.empresa["servicos"])
        return self.empresa["respostas"]["agendamento_iniciar"].format(lista_servicos=lista_servicos)

    def _handle_agendamento_servico(self, mensagem):
        for servico in self.empresa["servicos"]:
            if servico in mensagem.lower():
                self.dados_agendamento['servico'] = servico
                self.estado_conversa = 'agendando_dia_hora'
                return self.empresa["respostas"]["agendamento_pedir_data"].format(servico=servico)
        
        lista_servicos = ", ".join(self.empresa["servicos"])
        return self.empresa["respostas"]["agendamento_servico_invalido"].format(lista_servicos=lista_servicos)

    def _handle_agendamento_dia_hora(self, mensagem):
        match = re.search(r"(.*?) (?:às|as|de) (\d{1,2}(?::\d{2})?h?)", mensagem.lower())
        if match:
            dia = match.group(1).strip()
            hora = match.group(2).strip()
            servico = self.dados_agendamento.get('servico', 'serviço')
            
            self.estado_conversa = 'aguardando_confirmacao_final'
            return self.empresa["respostas"]["agendamento_confirmar"].format(servico=servico, dia=dia, hora=hora)
        else:
            return self.empresa["respostas"]["agendamento_data_invalida"]

    def _handle_confirmacao_final(self, mensagem):
        intencoes = self._detectar_intencoes(mensagem)
        self._resetar_estado() # Reseta o estado em qualquer resposta aqui

        if 'confirmacao_positiva' in intencoes:
            return self.empresa["respostas"]["confirmacao_final_positiva"]
        if 'confirmacao_negativa' in intencoes:
            return self.empresa["respostas"]["confirmacao_final_negativa"]
        
        # Se a resposta não for nem positiva nem negativa, tenta processar como uma nova requisição
        return self.processar(mensagem)
