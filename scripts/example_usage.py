"""
Exemplo de uso do sistema completo.
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rag.vector_store import VectorStore
from rag.sparql_query import SPARQLQueryEngine
from rag.hybrid_retriever import HybridRetriever
from agents.orchestrator import AgentOrchestrator


def example_1_basic_query():
    """Exemplo 1: Query básica através do orquestrador."""
    print("\n" + "="*60)
    print("Exemplo 1: Query Básica")
    print("="*60)
    
    # Inicializar componentes
    vector_store = VectorStore()
    vector_store.load()
    
    sparql_engine = SPARQLQueryEngine()
    retriever = HybridRetriever(vector_store, sparql_engine)
    orchestrator = AgentOrchestrator(retriever)
    
    # Processar query
    query = "Quais cursos estão disponíveis para o estudante Ana?"
    result = orchestrator.process_query(query)
    
    print(f"\nQuery: {query}")
    print(f"\nAgente: {result['agent']}")
    print(f"\nResposta:\n{result['response']}")
    print(f"\nCitações:")
    print(f"  Documentos: {len(result['citations'].get('documents', []))}")
    print(f"  IRIs: {len(result['citations'].get('iris', []))}")


def example_2_recommendation():
    """Exemplo 2: Sistema de recomendação."""
    print("\n" + "="*60)
    print("Exemplo 2: Recomendação")
    print("="*60)
    
    vector_store = VectorStore()
    vector_store.load()
    
    sparql_engine = SPARQLQueryEngine()
    retriever = HybridRetriever(vector_store, sparql_engine)
    orchestrator = AgentOrchestrator(retriever)
    
    query = "Recomende recursos sobre ontologias para o estudante Ana"
    context = {
        'student_id': 'http://www.exemplo.org/ead-ontologia#Estudante_Ana'
    }
    
    result = orchestrator.process_query(query, context)
    
    print(f"\nQuery: {query}")
    print(f"\nResposta:\n{result['response']}")


def example_3_sparql_direct():
    """Exemplo 3: Consulta SPARQL direta."""
    print("\n" + "="*60)
    print("Exemplo 3: Consulta SPARQL Direta")
    print("="*60)
    
    engine = SPARQLQueryEngine()
    
    query = """
    PREFIX ead: <http://www.exemplo.org/ead-ontologia#>
    SELECT ?estudante ?curso ?titulo
    WHERE {
        ?estudante a ead:Estudante .
        ?estudante ead:matriculadoEm ?curso .
        ?curso ead:temTitulo ?titulo .
    }
    """
    
    results = engine.query(query)
    
    print(f"\nQuery SPARQL executada")
    print(f"Resultados: {len(results)}")
    for result in results:
        print(f"  {result.get('estudante', 'N/A')} → {result.get('titulo', 'N/A')}")


def example_4_hybrid_retrieval():
    """Exemplo 4: Recuperação híbrida."""
    print("\n" + "="*60)
    print("Exemplo 4: Recuperação Híbrida")
    print("="*60)
    
    vector_store = VectorStore()
    vector_store.load()
    
    sparql_engine = SPARQLQueryEngine()
    retriever = HybridRetriever(vector_store, sparql_engine)
    
    query = "Como funcionam sistemas RAG?"
    results = retriever.retrieve(query, k=3)
    
    print(f"\nQuery: {query}")
    print(f"\nResultados Vetoriais: {len(results['vector_results'])}")
    for i, result in enumerate(results['vector_results'][:2], 1):
        print(f"\n  Documento {i} (score: {result['score']:.3f}):")
        print(f"  {result['document'].page_content[:200]}...")
    
    print(f"\nResultados SPARQL: {len(results['sparql_results'])}")
    for i, result in enumerate(results['sparql_results'][:2], 1):
        print(f"\n  Entidade {i}:")
        for key, value in list(result.items())[:3]:
            print(f"    {key}: {value}")


def main():
    """Executa todos os exemplos."""
    print("\n" + "="*60)
    print("EXEMPLOS DE USO DO SISTEMA")
    print("="*60)
    
    try:
        example_1_basic_query()
        example_2_recommendation()
        example_3_sparql_direct()
        example_4_hybrid_retrieval()
        
        print("\n" + "="*60)
        print("Todos os exemplos executados com sucesso!")
        print("="*60)
    except Exception as e:
        print(f"\nErro durante execução: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

