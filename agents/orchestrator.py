"""
Orquestrador usando LangGraph para coordenar múltiplos agentes.
"""
from typing import Dict, Any, List, TypedDict, Annotated
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langchain_core.messages import HumanMessage, AIMessage
from agents.coordinator import CoordinatorAgent
from agents.student import StudentAgent
from agents.recommendation import RecommendationAgent
from agents.lms import LMSAgent
from rag.hybrid_retriever import HybridRetriever


class AgentState(TypedDict):
    """Estado compartilhado entre agentes."""
    messages: Annotated[List[Dict], add_messages]
    query: str
    current_agent: str
    context: Dict[str, Any]
    citations: Dict[str, List]
    history: List[Dict]


class AgentOrchestrator:
    """Orquestrador de agentes usando LangGraph."""
    
    def __init__(self, retriever: HybridRetriever):
        """
        Inicializa o orquestrador.
        
        Args:
            retriever: Retriever híbrido compartilhado
        """
        self.retriever = retriever
        
        # Inicializar agentes
        self.coordinator = CoordinatorAgent(retriever)
        self.lms_agent = LMSAgent(retriever=retriever)
        self.recommendation_agent = RecommendationAgent(retriever)
        
        # Estudantes serão criados dinamicamente
        self.student_agents: Dict[str, StudentAgent] = {}
        
        # Construir grafo
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Constrói o grafo de estados dos agentes."""
        workflow = StateGraph(AgentState)
        
        # Adicionar nós
        workflow.add_node("coordinator", self._coordinator_node)
        workflow.add_node("lms", self._lms_node)
        workflow.add_node("recommendation", self._recommendation_node)
        workflow.add_node("student", self._student_node)
        workflow.add_node("router", self._router_node)
        
        # Definir ponto de entrada
        workflow.set_entry_point("router")
        
        # Definir transições
        workflow.add_conditional_edges(
            "router",
            self._route_query,
            {
                "coordinator": "coordinator",
                "lms": "lms",
                "recommendation": "recommendation",
                "student": "student"
            }
        )
        
        # Todos os nós retornam ao coordenador para finalizar
        workflow.add_edge("coordinator", END)
        workflow.add_edge("lms", END)
        workflow.add_edge("recommendation", END)
        workflow.add_edge("student", END)
        
        return workflow.compile()
    
    def _router_node(self, state: AgentState) -> AgentState:
        """Nó roteador que decide qual agente processar."""
        return state
    
    def _route_query(self, state: AgentState) -> str:
        """
        Roteia a query para o agente apropriado.
        
        Args:
            state: Estado atual
            
        Returns:
            Nome do agente para processar
        """
        query = state.get("query", "").lower()
        
        # Detectar tipo de consulta com melhor lógica
        # Perguntas conceituais/explicativas (como, o que, por que, explique)
        conceptual_keywords = ['como', 'o que', 'o que é', 'por que', 'explique', 'explique-me', 
                              'defina', 'definição', 'conceito', 'funciona', 'funcionam',
                              'rag', 'ontologia', 'sparql', 'inferência', 'reasoner']
        
        # Recomendações
        recommendation_keywords = ['recomendar', 'recomendação', 'sugerir', 'sugestão', 
                                  'recomende', 'sugira', 'indique']
        
        # Consultas específicas sobre cursos/tarefas/recursos da plataforma
        lms_keywords = ['curso específico', 'tarefa específica', 'recurso específico',
                       'quais cursos', 'quais tarefas', 'quais recursos',
                       'curso do estudante', 'tarefa do estudante']
        
        # Consultas sobre estudantes específicos
        student_keywords = ['estudante', 'student', 'aluno', 'minhas tarefas', 
                          'meus cursos', 'minha matrícula']
        
        # Verificar perguntas conceituais primeiro (mais específico)
        if any(keyword in query for keyword in conceptual_keywords):
            return "coordinator"  # CoordinatorAgent lida melhor com perguntas conceituais
        
        # Verificar recomendações
        if any(keyword in query for keyword in recommendation_keywords):
            return "recommendation"
        
        # Verificar consultas específicas sobre estudantes
        if any(keyword in query for keyword in student_keywords):
            return "student"
        
        # Verificar consultas específicas sobre cursos/tarefas/recursos
        if any(keyword in query for keyword in lms_keywords):
            return "lms"
        
        # Fallback: perguntas gerais vão para coordinator
        return "coordinator"
    
    def _coordinator_node(self, state: AgentState) -> AgentState:
        """Nó do coordenador."""
        query = state.get("query", "")
        try:
            response = self.coordinator.process(query, state.get("context"))
            content = response.get("content", "Sem resposta disponível.")
            citations = response.get("citations", {})
            current_agent = "coordinator"
        except Exception as e:
            # Log do erro para debug
            error_msg = str(e)
            print(f"⚠️  Erro no CoordinatorAgent: {error_msg}")
            print(f"   Query: {query[:100]}...")
            
            # Se for erro de LLM não disponível, dar mensagem clara
            if "LLM" in error_msg or "ollama" in error_msg.lower() or "openai" in error_msg.lower():
                content = f"""⚠️ Erro: LLM não está configurado ou não está disponível.

Erro: {error_msg}

Por favor:
1. Configure Ollama: `USE_OLLAMA=true` no arquivo .env
2. Inicie Ollama: `ollama serve` em um terminal separado
3. Ou configure OpenAI: `OPENAI_API_KEY=sua_chave` no arquivo .env

Sem LLM, não posso gerar respostas em linguagem natural."""
                citations = {}
                current_agent = "coordinator_error"
            else:
                # Outros erros: tentar fallback mas informar
                try:
                    print("   Tentando fallback com LMSAgent...")
                    response = self.lms_agent.process(query, state.get("context"))
                    content = response.get("content", "Sem resposta disponível.")
                    citations = response.get("citations", {})
                    current_agent = "lms_fallback"
                    # Adicionar nota sobre o fallback
                    if "Como LMSAgent" in content:
                        content += "\n\n(Nota: Esta pergunta conceitual foi redirecionada. Para respostas mais detalhadas, configure o LLM.)"
                except Exception as e2:
                    content = f"""Erro ao processar consulta.

Erro no CoordinatorAgent: {error_msg}
Erro no fallback: {str(e2)}

Por favor, verifique:
- Se o LLM está configurado (Ollama ou OpenAI)
- Se há documentos carregados no vector store
- Se a ontologia está acessível"""
                    citations = {}
                    current_agent = "error"
        
        # Adicionar mensagem usando objeto AIMessage (compatível com add_messages)
        state["messages"].append(AIMessage(content=content))
        state["citations"] = citations
        state["current_agent"] = current_agent
        
        return state
    
    def _lms_node(self, state: AgentState) -> AgentState:
        """Nó do LMS."""
        query = state.get("query", "")
        try:
            response = self.lms_agent.process(query, state.get("context"))
            content = response.get("content", "Sem resposta disponível.")
        except Exception as e:
            # Fallback se houver erro
            content = f"Erro ao processar: {str(e)}"
            response = {"citations": {}}
        
        # Adicionar mensagem usando objeto AIMessage
        state["messages"].append(AIMessage(content=content))
        state["citations"] = response.get("citations", {})
        state["current_agent"] = "lms"
        
        return state
    
    def _recommendation_node(self, state: AgentState) -> AgentState:
        """Nó de recomendação."""
        query = state.get("query", "")
        response = self.recommendation_agent.process(query, state.get("context"))
        
        # Adicionar mensagem usando objeto AIMessage
        state["messages"].append(AIMessage(content=response["content"]))
        state["citations"] = response.get("citations", {})
        state["current_agent"] = "recommendation"
        
        return state
    
    def _student_node(self, state: AgentState) -> AgentState:
        """Nó do estudante."""
        query = state.get("query", "")
        context = state.get("context", {})
        
        # Obter ou criar agente estudante
        student_id = context.get("student_id", "Estudante_Ana")
        if student_id not in self.student_agents:
            self.student_agents[student_id] = StudentAgent(
                student_id, 
                self.retriever
            )
        
        student_agent = self.student_agents[student_id]
        response = student_agent.process(query, context)
        
        # Adicionar mensagem usando objeto AIMessage
        state["messages"].append(AIMessage(content=response["content"]))
        state["citations"] = response.get("citations", {})
        state["current_agent"] = f"student_{student_id}"
        
        return state
    
    def process_query(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Processa uma query através do orquestrador.
        
        Args:
            query: Query do usuário
            context: Contexto adicional
            
        Returns:
            Resposta com citações
        """
        initial_state: AgentState = {
            "messages": [HumanMessage(content=query)],
            "query": query,
            "current_agent": "",
            "context": context or {},
            "citations": {"documents": [], "iris": []},
            "history": []
        }
        
        # Executar grafo
        final_state = self.graph.invoke(initial_state)
        
        # Extrair resposta final
        messages = final_state.get("messages", [])
        last_message = messages[-1] if messages else None
        
        # Acessar conteúdo da mensagem (pode ser AIMessage ou dict)
        if last_message:
            if hasattr(last_message, 'content'):
                response_content = last_message.content
            elif isinstance(last_message, dict):
                response_content = last_message.get("content", "")
            else:
                response_content = str(last_message)
        else:
            response_content = ""
        
        return {
            "response": response_content,
            "agent": final_state.get("current_agent", "unknown"),
            "citations": final_state.get("citations", {}),
            "history": [msg.content if hasattr(msg, 'content') else (msg.get("content", "") if isinstance(msg, dict) else str(msg)) for msg in messages]
        }

