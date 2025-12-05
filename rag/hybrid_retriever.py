"""
Módulo para RAG híbrido combinando busca vetorial e SPARQL.
"""
from typing import List, Dict, Optional
from rag.vector_store import VectorStore
from rag.sparql_query import SPARQLQueryEngine


class HybridRetriever:
    """Retriever híbrido que combina busca vetorial e consultas SPARQL."""
    
    def __init__(self, vector_store: VectorStore, sparql_engine: SPARQLQueryEngine):
        """
        Inicializa o retriever híbrido.
        
        Args:
            vector_store: Instância do VectorStore
            sparql_engine: Instância do SPARQLQueryEngine
        """
        self.vector_store = vector_store
        self.sparql_engine = sparql_engine
    
    def retrieve(self, query: str, k: int = 5, use_sparql: bool = True, 
                 filters: Optional[Dict] = None) -> Dict:
        """
        Recupera informações usando busca híbrida.
        
        Args:
            query: Consulta do usuário
            k: Número de resultados da busca vetorial
            use_sparql: Se deve usar consultas SPARQL
            filters: Filtros opcionais
            
        Returns:
            Dicionário com resultados vetoriais e SPARQL, além de citações
        """
        results = {
            'vector_results': [],
            'sparql_results': [],
            'citations': {
                'documents': [],
                'iris': []
            },
            'combined_context': ""
        }
        
        # 1. Busca vetorial em documentos
        vector_results = self.vector_store.search(query, k=k, filters=filters)
        results['vector_results'] = vector_results
        
        # Extrair citações de documentos
        for result in vector_results:
            doc_meta = result['metadata']
            citation = {
                'type': 'document',
                'source': doc_meta.get('source', 'unknown'),
                'chunk': result['document'].page_content[:200] + "...",
                'score': result['score']
            }
            results['citations']['documents'].append(citation)
        
        # 2. Consultas SPARQL (se habilitado)
        if use_sparql:
            sparql_results = self._extract_sparql_info(query)
            results['sparql_results'] = sparql_results
            
            # Extrair IRIs como citações
            for result in sparql_results:
                for key, value in result.items():
                    if isinstance(value, str) and value.startswith('http://'):
                        citation = {
                            'type': 'iri',
                            'iri': value,
                            'property': key
                        }
                        if citation not in results['citations']['iris']:
                            results['citations']['iris'].append(citation)
        
        # 3. Combinar contexto
        results['combined_context'] = self._combine_context(
            vector_results, 
            sparql_results if use_sparql else []
        )
        
        return results
    
    def _extract_sparql_info(self, query: str) -> List[Dict]:
        """
        Extrai informações relevantes da ontologia baseado na query.
        
        Args:
            query: Consulta do usuário
            
        Returns:
            Lista de resultados SPARQL
        """
        results = []
        
        # Detectar tipo de consulta baseado em palavras-chave
        query_lower = query.lower()
        
        # Consultas sobre cursos
        if any(word in query_lower for word in ['curso', 'course', 'disciplina']):
            if 'estudante' in query_lower or 'student' in query_lower:
                # Tentar extrair IRI do estudante da query ou usar padrão
                student_id = self._extract_entity_iri(query, 'Estudante')
                if student_id:
                    results.extend(self.sparql_engine.get_courses(student_id))
                else:
                    results.extend(self.sparql_engine.get_courses())
            else:
                results.extend(self.sparql_engine.get_courses())
        
        # Consultas sobre tarefas
        if any(word in query_lower for word in ['tarefa', 'task', 'atividade']):
            student_id = self._extract_entity_iri(query, 'Estudante')
            if student_id:
                results.extend(self.sparql_engine.get_student_tasks(student_id))
        
        # Consultas sobre recursos
        if any(word in query_lower for word in ['recurso', 'resource', 'material', 'vídeo', 'video']):
            course_id = self._extract_entity_iri(query, 'Curso')
            if course_id:
                results.extend(self.sparql_engine.get_resources_for_course(course_id))
        
        # Consultas sobre feedback
        if any(word in query_lower for word in ['feedback', 'avaliação', 'evaluation']):
            student_id = self._extract_entity_iri(query, 'Estudante')
            if student_id:
                results.extend(self.sparql_engine.get_feedback(student_id))
        
        # Consultas sobre competências
        if any(word in query_lower for word in ['competência', 'competency', 'habilidade', 'skill']):
            course_id = self._extract_entity_iri(query, 'Curso')
            if course_id:
                results.extend(self.sparql_engine.get_competencies_for_course(course_id))
        
        return results
    
    def _extract_entity_iri(self, query: str, entity_type: str) -> Optional[str]:
        """
        Tenta extrair o IRI de uma entidade da query.
        
        Args:
            query: Consulta do usuário
            entity_type: Tipo da entidade (ex: 'Estudante', 'Curso')
            
        Returns:
            IRI da entidade ou None
        """
        # Mapeamento de nomes para IRIs conhecidos
        entity_map = {
            'Estudante': {
                'ana': 'http://www.exemplo.org/ead-ontologia#Estudante_Ana',
                'estudante_ana': 'http://www.exemplo.org/ead-ontologia#Estudante_Ana',
            },
            'Curso': {
                'curso1': 'http://www.exemplo.org/ead-ontologia#Curso1',
                'curso 1': 'http://www.exemplo.org/ead-ontologia#Curso1',
            }
        }
        
        query_lower = query.lower()
        
        if entity_type in entity_map:
            for key, iri in entity_map[entity_type].items():
                if key in query_lower:
                    return iri
        
        return None
    
    def _combine_context(self, vector_results: List[Dict], sparql_results: List[Dict]) -> str:
        """
        Combina resultados vetoriais e SPARQL em um contexto único.
        
        Args:
            vector_results: Resultados da busca vetorial
            sparql_results: Resultados das consultas SPARQL
            
        Returns:
            Contexto combinado como string
        """
        context_parts = []
        
        # Adicionar contexto dos documentos
        if vector_results:
            context_parts.append("=== Informações de Documentos ===\n")
            for i, result in enumerate(vector_results[:3], 1):
                doc_content = result['document'].page_content
                context_parts.append(f"Documento {i} (score: {result['score']:.3f}):\n{doc_content}\n")
        
        # Adicionar contexto da ontologia
        if sparql_results:
            context_parts.append("\n=== Informações da Ontologia ===\n")
            for i, result in enumerate(sparql_results[:5], 1):
                context_parts.append(f"Entidade {i}:\n")
                for key, value in result.items():
                    context_parts.append(f"  {key}: {value}\n")
                context_parts.append("\n")
        
        return "\n".join(context_parts)
    
    def verify_consistency(self, claim: Dict) -> Dict:
        """
        Verifica consistência ontológica de uma afirmação.
        
        Args:
            claim: Afirmação a verificar com campos: entity, property, value
            
        Returns:
            Resultado da verificação de consistência
        """
        entity_iri = claim.get('entity')
        property_iri = claim.get('property')
        value = claim.get('value')
        
        if not all([entity_iri, property_iri, value]):
            return {
                'consistent': False,
                'reason': 'Campos obrigatórios faltando'
            }
        
        is_consistent = self.sparql_engine.check_consistency(
            entity_iri, property_iri, value
        )
        
        return {
            'consistent': is_consistent,
            'entity': entity_iri,
            'property': property_iri,
            'value': value
        }

