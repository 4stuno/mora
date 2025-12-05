"""
RecommendationAgent - Fornece recomendações personalizadas.
"""
from typing import Dict, Any, Optional, List
from agents.base_agent import BaseAgent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage


class RecommendationAgent(BaseAgent):
    """Agente que fornece recomendações baseadas em competências e resultados de aprendizagem."""
    
    def __init__(self, retriever=None, model_name: str = "gpt-4"):
        super().__init__("RecommendationAgent", retriever, model_name)
        
        self.system_prompt = """Você é o RecommendationAgent de um sistema multiagente para plataforma de ensino.

Suas responsabilidades incluem:
- Fornecer feedback personalizado
- Sugerir recursos (Recurso) ou cursos (Curso) baseado em:
  * ResultadoDeAprendizagem
  * Competencia
  * Histórico do estudante
  * Desempenho em avaliações

Você consulta a ontologia usando SPARQL para:
- Identificar competências necessárias
- Encontrar recursos relacionados
- Verificar pré-requisitos de cursos

Sempre forneça justificativas baseadas em dados da ontologia.
Cite IRIs e documentos em suas recomendações."""
        
        self.prompt_template = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}")
        ])
    
    def process(self, message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Processa solicitação de recomendação.
        
        Args:
            message: Mensagem com solicitação
            context: Contexto adicional (ex: student_id, course_id)
            
        Returns:
            Recomendações com justificativas e citações
        """
        # Adicionar contexto à query
        query = message
        if context:
            if 'student_id' in context:
                query += f" estudante {context['student_id']}"
            if 'course_id' in context:
                query += f" curso {context['course_id']}"
        
        # Recuperar contexto usando RAG híbrido
        rag_context = self._retrieve_context(query)
        
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
        
        # Gerar recomendação
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
    
    def recommend_resources(self, student_id: str, topic: str) -> Dict[str, Any]:
        """
        Recomenda recursos para um estudante sobre um tópico.
        
        Args:
            student_id: IRI do estudante
            topic: Tópico de interesse
            
        Returns:
            Recomendações de recursos
        """
        message = f"Recomende recursos sobre {topic}"
        context = {'student_id': student_id}
        return self.process(message, context)
    
    def recommend_courses(self, student_id: str, competencies: List[str]) -> Dict[str, Any]:
        """
        Recomenda cursos baseado em competências.
        
        Args:
            student_id: IRI do estudante
            competencies: Lista de competências desejadas
            
        Returns:
            Recomendações de cursos
        """
        message = f"Recomende cursos que desenvolvam as competências: {', '.join(competencies)}"
        context = {'student_id': student_id}
        return self.process(message, context)

