"""
Classe base para agentes do sistema.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import os
from rag.hybrid_retriever import HybridRetriever

# Tentar importar diferentes tipos de LLM
try:
    from langchain_ollama import ChatOllama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False

try:
    from langchain_openai import ChatOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    from langchain_community.llms import LlamaCpp
    LLAMACPP_AVAILABLE = True
except ImportError:
    LLAMACPP_AVAILABLE = False


def _get_llm(model_name: str = None, temperature: float = 0.7):
    """
    Obtém o LLM apropriado baseado na configuração.
    
    Prioridade:
    1. Ollama (se disponível e configurado)
    2. OpenAI (se API key disponível)
    3. LlamaCpp (se disponível)
    """
    # Verificar variáveis de ambiente
    use_ollama = os.getenv("USE_OLLAMA", "false").lower() == "true"
    ollama_model = os.getenv("OLLAMA_MODEL", "llama3.2")
    openai_key = os.getenv("OPENAI_API_KEY")
    
    # Prioridade 1: Ollama (local, gratuito)
    if use_ollama and OLLAMA_AVAILABLE:
        try:
            return ChatOllama(model=ollama_model, temperature=temperature)
        except Exception as e:
            print(f"Aviso: Não foi possível conectar ao Ollama: {e}")
            print("Certifique-se de que o Ollama está rodando: ollama serve")
    
    # Prioridade 2: OpenAI (se API key disponível)
    if openai_key and OPENAI_AVAILABLE:
        model = model_name or os.getenv("OPENAI_MODEL", "gpt-4")
        return ChatOpenAI(model=model, temperature=temperature)
    
    # Prioridade 3: LlamaCpp (local, se disponível)
    if LLAMACPP_AVAILABLE:
        model_path = os.getenv("LLAMA_MODEL_PATH")
        if model_path and os.path.exists(model_path):
            return LlamaCpp(
                model_path=model_path,
                temperature=temperature,
                n_ctx=2048,
                verbose=False
            )
    
    # Fallback: Tentar Ollama mesmo sem configuração explícita
    if OLLAMA_AVAILABLE:
        try:
            return ChatOllama(model="llama3.2", temperature=temperature)
        except:
            pass
    
    # Se nada funcionar, levantar erro informativo
    raise RuntimeError(
        "Nenhum LLM disponível! Configure uma das opções:\n"
        "1. Ollama (recomendado, gratuito): USE_OLLAMA=true OLLAMA_MODEL=llama3.2\n"
        "2. OpenAI: OPENAI_API_KEY=sua_chave\n"
        "3. LlamaCpp: LLAMA_MODEL_PATH=caminho/para/modelo.gguf"
    )


class BaseAgent(ABC):
    """Classe base abstrata para todos os agentes."""
    
    def __init__(self, name: str, retriever: Optional[HybridRetriever] = None,
                 model_name: str = None, temperature: float = 0.7):
        """
        Inicializa o agente base.
        
        Args:
            name: Nome do agente
            retriever: Retriever híbrido (opcional)
            model_name: Nome do modelo LLM (opcional, usa configuração de ambiente)
            temperature: Temperatura para o LLM
        """
        self.name = name
        self.retriever = retriever
        self.llm = _get_llm(model_name, temperature)
        self.conversation_history: list = []
    
    @abstractmethod
    def process(self, message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Processa uma mensagem e retorna uma resposta.
        
        Args:
            message: Mensagem a processar
            context: Contexto adicional (opcional)
            
        Returns:
            Resposta do agente com citações
        """
        pass
    
    def _retrieve_context(self, query: str) -> Dict:
        """Recupera contexto usando o retriever híbrido."""
        if self.retriever:
            return self.retriever.retrieve(query)
        return {}
    
    def _format_response(self, content: str, citations: Dict) -> Dict[str, Any]:
        """
        Formata resposta com citações.
        
        Args:
            content: Conteúdo da resposta
            citations: Citações (documentos e IRIs)
            
        Returns:
            Resposta formatada
        """
        return {
            'agent': self.name,
            'content': content,
            'citations': citations,
            'timestamp': self._get_timestamp()
        }
    
    def _get_timestamp(self) -> str:
        """Retorna timestamp atual."""
        from datetime import datetime
        return datetime.now().isoformat()

