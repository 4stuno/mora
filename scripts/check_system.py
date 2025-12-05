"""
Script para verificar o estado do sistema RAG.
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rag.vector_store import VectorStore
from rag.sparql_query import SPARQLQueryEngine
from rag.hybrid_retriever import HybridRetriever
from agents.base_agent import _get_llm

def check_vector_store():
    """Verifica se há documentos no vector store."""
    print("\n=== Verificando Vector Store ===")
    vector_store = VectorStore()
    
    # Tentar carregar
    try:
        vector_store.load()
        num_docs = len(vector_store.documents)
        print(f"✓ Vector store carregado")
        print(f"  Documentos/chunks: {num_docs}")
        
        if num_docs == 0:
            print("  ⚠️  NENHUM DOCUMENTO ENCONTRADO!")
            print("  Execute: python scripts/load_documents.py")
            return False
        
        # Testar busca
        test_query = "RAG sistemas"
        results = vector_store.search(test_query, k=3)
        print(f"  Teste de busca ('{test_query}'): {len(results)} resultados")
        
        return True
    except Exception as e:
        print(f"  ✗ Erro ao carregar vector store: {e}")
        return False

def check_sparql():
    """Verifica se SPARQL está funcionando."""
    print("\n=== Verificando SPARQL ===")
    try:
        engine = SPARQLQueryEngine()
        query = """
        PREFIX ead: <http://www.exemplo.org/ead-ontologia#>
        SELECT (COUNT(?curso) as ?total)
        WHERE {
            ?curso a ead:Curso .
        }
        """
        results = engine.query(query)
        print(f"✓ SPARQL funcionando")
        print(f"  Cursos na ontologia: {len(results)}")
        return True
    except Exception as e:
        print(f"  ✗ Erro no SPARQL: {e}")
        return False

def check_llm():
    """Verifica se LLM está disponível."""
    print("\n=== Verificando LLM ===")
    try:
        llm = _get_llm()
        print(f"✓ LLM disponível: {type(llm).__name__}")
        return True
    except Exception as e:
        print(f"  ✗ LLM não disponível: {e}")
        print("  Configure:")
        print("    - Ollama: USE_OLLAMA=true e 'ollama serve'")
        print("    - Ou OpenAI: OPENAI_API_KEY=sua_chave")
        return False

def check_hybrid_retriever():
    """Verifica se o retriever híbrido está funcionando."""
    print("\n=== Verificando Hybrid Retriever ===")
    try:
        vector_store = VectorStore()
        vector_store.load()
        sparql_engine = SPARQLQueryEngine()
        retriever = HybridRetriever(vector_store, sparql_engine)
        
        test_query = "Como funcionam sistemas RAG?"
        results = retriever.retrieve(test_query, k=3)
        
        print(f"✓ Hybrid Retriever funcionando")
        print(f"  Resultados vetoriais: {len(results.get('vector_results', []))}")
        print(f"  Resultados SPARQL: {len(results.get('sparql_results', []))}")
        print(f"  Citações documentos: {len(results.get('citations', {}).get('documents', []))}")
        print(f"  Citações IRIs: {len(results.get('citations', {}).get('iris', []))}")
        
        if results.get('combined_context'):
            print(f"  Contexto combinado: {len(results['combined_context'])} caracteres")
        
        return True
    except Exception as e:
        print(f"  ✗ Erro no Hybrid Retriever: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Executa todas as verificações."""
    print("=" * 60)
    print("DIAGNÓSTICO DO SISTEMA RAG")
    print("=" * 60)
    
    results = {
        'vector_store': check_vector_store(),
        'sparql': check_sparql(),
        'llm': check_llm(),
        'hybrid_retriever': check_hybrid_retriever()
    }
    
    print("\n" + "=" * 60)
    print("RESUMO")
    print("=" * 60)
    
    all_ok = all(results.values())
    
    for component, status in results.items():
        status_symbol = "✓" if status else "✗"
        print(f"{status_symbol} {component}: {'OK' if status else 'PROBLEMA'}")
    
    if all_ok:
        print("\n✅ Sistema está pronto para uso!")
    else:
        print("\n⚠️  Há problemas que precisam ser corrigidos:")
        if not results['vector_store']:
            print("  1. Execute: python scripts/load_documents.py")
        if not results['llm']:
            print("  2. Configure LLM (Ollama ou OpenAI)")

if __name__ == "__main__":
    main()

