"""
StudentAgent - Representa estudantes e suas ações.
"""
from typing import Dict, Any, Optional
from agents.base_agent import BaseAgent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage


class StudentAgent(BaseAgent):
    """Agente que representa um estudante."""
    
    def __init__(self, student_id: str, retriever=None, model_name: str = "gpt-4"):
        """
        Inicializa o agente estudante.
        
        Args:
            student_id: IRI do estudante na ontologia
            retriever: Retriever híbrido
            model_name: Nome do modelo LLM
        """
        super().__init__(f"StudentAgent_{student_id}", retriever, model_name)
        self.student_id = student_id
        
        self.system_prompt = f"""Você é o StudentAgent representando o estudante {student_id} em um sistema multiagente para plataforma de ensino.

Suas responsabilidades incluem:
- Executar tarefas atribuídas
- Interagir com recursos disponíveis
- Solicitar ajuda quando necessário
- Receber e processar recomendações

Você percebe:
- Recursos disponíveis (Recurso, Video, Apresentacao)
- Tarefas atribuídas (Tarefa)
- Avaliações pendentes (Avaliacao)

Sempre cite suas fontes usando IRIs da ontologia e documentos quando disponíveis.
Verifique consistência ontológica antes de fazer afirmações sobre suas ações."""
        
        self.prompt_template = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}")
        ])
    
    def process(self, message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Processa mensagem do estudante.
        
        Args:
            message: Mensagem a processar
            context: Contexto adicional
            
        Returns:
            Resposta do estudante com citações
        """
        # Recuperar contexto específico do estudante
        query_with_context = f"{message} estudante {self.student_id}"
        rag_context = self._retrieve_context(query_with_context)
        
        # Preparar histórico
        messages = []
        for msg in self.conversation_history[-5:]:
            if msg['role'] == 'user':
                messages.append(HumanMessage(content=msg['content']))
            else:
                messages.append(AIMessage(content=msg['content']))
        
        # Adicionar contexto recuperado
        context_text = ""
        if rag_context.get('combined_context'):
            context_text = f"\n\nContexto recuperado:\n{rag_context['combined_context']}"
        
        # Gerar resposta
        response = self.llm.invoke(
            self.prompt_template.format_messages(
                chat_history=messages,
                input=message + context_text
            )
        )
        
        # Extrair citações
        citations = {
            'documents': rag_context.get('citations', {}).get('documents', []),
            'iris': rag_context.get('citations', {}).get('iris', [])
        }
        
        # Atualizar histórico
        self.conversation_history.append({'role': 'user', 'content': message})
        self.conversation_history.append({'role': 'assistant', 'content': response.content})
        
        return self._format_response(response.content, citations)
    
    def request_extension(self, task_id: str, reason: str) -> Dict[str, Any]:
        """
        Solicita extensão de prazo para uma tarefa.
        
        Args:
            task_id: IRI da tarefa
            reason: Razão da solicitação
            
        Returns:
            Solicitação formatada
        """
        message = f"Solicito extensão de prazo para a tarefa {task_id}. Razão: {reason}"
        return self.process(message)

