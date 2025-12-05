"""
CoordinatorAgent - Orquestra tarefas e resolve conflitos.
"""
from typing import Dict, Any, Optional
from agents.base_agent import BaseAgent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage


class CoordinatorAgent(BaseAgent):
    """Agente coordenador que gerencia fluxo de tarefas."""
    
    def __init__(self, retriever=None, model_name: str = "gpt-4"):
        super().__init__("CoordinatorAgent", retriever, model_name)
        
        self.system_prompt = """Você é o CoordinatorAgent de um sistema multiagente para plataforma de ensino.
        
Suas responsabilidades incluem:
- Responder perguntas conceituais e explicativas sobre o sistema, tecnologias e conceitos relacionados
- Gerenciar fluxo de tarefas (publicação de material, abertura de avaliações)
- Resolver conflitos de agenda
- Iniciar protocolos de negociação (ex: mudar prazo de entrega)
- Coordenar comunicação entre agentes

Você pode explicar conceitos como:
- RAG (Retrieval-Augmented Generation): sistemas que combinam busca em documentos com geração de texto
- Ontologias OWL 2 DL e inferência lógica
- SPARQL e consultas a grafos de conhecimento
- Sistemas multiagente e orquestração
- Integração de diferentes fontes de conhecimento

Você usa a ontologia para raciocinar sobre:
- Cronograma, Sessao, temDataInicio, temDuracao, temPapel
- Relações entre cursos, estudantes, professores e tarefas

Sempre cite suas fontes usando IRIs da ontologia e documentos quando disponíveis.
Verifique consistência ontológica antes de fazer afirmações.
Seja detalhado e educativo em suas explicações."""
        
        self.prompt_template = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}")
        ])
    
    def process(self, message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Processa mensagem e coordena ações.
        
        Args:
            message: Mensagem a processar
            context: Contexto adicional
            
        Returns:
            Resposta coordenada com citações
        """
        # Recuperar contexto usando RAG híbrido
        rag_context = self._retrieve_context(message)
        
        # Preparar histórico de conversa
        messages = []
        for msg in self.conversation_history[-5:]:  # Últimas 5 mensagens
            if msg['role'] == 'user':
                messages.append(HumanMessage(content=msg['content']))
            else:
                messages.append(AIMessage(content=msg['content']))
        
        # Adicionar contexto recuperado
        context_text = ""
        if rag_context.get('combined_context'):
            context_text = f"\n\nContexto recuperado:\n{rag_context['combined_context']}"
        
        # Adicionar inferências DL explícitas (se disponível)
        dl_inferences = ""
        try:
            from ontology.reasoner import DLReasoner
            reasoner = DLReasoner()
            consistency = reasoner.check_consistency()
            if consistency.get('consistent'):
                dl_inferences = "\n\n=== Inferências DL ===\n"
                dl_inferences += f"Ontologia consistente: ✅\n"
                # Adicionar tipos inferidos relevantes
                realization = reasoner.realize()
                if realization:
                    dl_inferences += f"Tipos inferidos disponíveis: {len(realization)} indivíduos\n"
                context_text += dl_inferences
        except:
            pass  # Se reasoner não disponível, continuar sem inferências
        
        # Gerar resposta usando LLM
        try:
            response = self.llm.invoke(
                self.prompt_template.format_messages(
                    chat_history=messages,
                    input=message + context_text
                )
            )
        except Exception as e:
            # Se LLM falhar, verificar se é problema de configuração
            error_msg = str(e).lower()
            if "connection" in error_msg or "refused" in error_msg or "timeout" in error_msg:
                raise RuntimeError(
                    f"LLM não está disponível. Verifique se Ollama está rodando (ollama serve) ou se a API key do OpenAI está configurada. Erro: {e}"
                )
            else:
                raise RuntimeError(f"Erro ao gerar resposta com LLM: {e}")
        
        # Extrair citações
        citations = {
            'documents': rag_context.get('citations', {}).get('documents', []),
            'iris': rag_context.get('citations', {}).get('iris', [])
        }
        
        # Atualizar histórico
        self.conversation_history.append({'role': 'user', 'content': message})
        self.conversation_history.append({'role': 'assistant', 'content': response.content})
        
        return self._format_response(response.content, citations)

