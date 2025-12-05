"""
Módulo para consultas SPARQL à ontologia.
"""
from typing import List, Dict, Optional
from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.plugins.sparql import prepareQuery
import os


def _get_ontology_path(ontology_path: str = "ontologia_mora.owl") -> str:
    """
    Resolve o caminho da ontologia relativo à raiz do projeto.
    
    Args:
        ontology_path: Caminho relativo ou absoluto para o arquivo OWL
        
    Returns:
        Caminho absoluto para o arquivo OWL
    """
    # Se já é um caminho absoluto, retornar como está
    if os.path.isabs(ontology_path):
        return ontology_path
    
    # Encontrar o diretório raiz do projeto (onde está ontologia_mora.owl)
    # Começar do diretório deste arquivo e subir até encontrar o arquivo
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Tentar encontrar o arquivo subindo os diretórios
    for _ in range(5):  # Limitar a busca a 5 níveis
        potential_path = os.path.join(current_dir, ontology_path)
        if os.path.exists(potential_path):
            return os.path.abspath(potential_path)
        parent_dir = os.path.dirname(current_dir)
        if parent_dir == current_dir:  # Chegou na raiz do sistema
            break
        current_dir = parent_dir
    
    # Se não encontrou, tentar caminho relativo ao diretório atual
    return os.path.abspath(ontology_path)


class SPARQLQueryEngine:
    """Motor de consultas SPARQL para a ontologia."""
    
    def __init__(self, ontology_path: str = "ontologia_mora.owl"):
        """
        Inicializa o motor de consultas SPARQL.
        
        Args:
            ontology_path: Caminho para o arquivo OWL
        """
        self.graph = Graph()
        resolved_path = _get_ontology_path(ontology_path)
        self.graph.parse(resolved_path, format="xml")
        
        # Definir namespaces
        self.EAD = Namespace("http://www.exemplo.org/ead-ontologia#")
        self.graph.bind("ead", self.EAD)
        
    def query(self, sparql_query: str) -> List[Dict]:
        """
        Executa uma consulta SPARQL.
        
        Args:
            sparql_query: Consulta SPARQL como string
            
        Returns:
            Lista de resultados como dicionários
        """
        results = []
        query_result = self.graph.query(sparql_query)
        
        for row in query_result:
            result_dict = {}
            for var in query_result.vars:
                value = row[var]
                if value:
                    if isinstance(value, URIRef):
                        result_dict[str(var)] = str(value)
                    elif isinstance(value, Literal):
                        result_dict[str(var)] = str(value.value)
                    else:
                        result_dict[str(var)] = str(value)
            results.append(result_dict)
        
        return results
    
    def get_courses(self, student_id: Optional[str] = None) -> List[Dict]:
        """
        Obtém cursos, opcionalmente filtrados por estudante.
        
        Args:
            student_id: IRI do estudante (opcional)
            
        Returns:
            Lista de cursos com metadados
        """
        if student_id:
            query = """
            PREFIX ead: <http://www.exemplo.org/ead-ontologia#>
            SELECT ?curso ?titulo ?descricao ?duracao ?professor
            WHERE {
                ?curso a ead:Curso .
                ?curso ead:temMatriculado <%s> .
                OPTIONAL { ?curso ead:temTitulo ?titulo . }
                OPTIONAL { ?curso ead:temDescricao ?descricao . }
                OPTIONAL { ?curso ead:temDuracao ?duracao . }
                OPTIONAL { ?curso ead:ministradoPor ?professor . }
            }
            """ % student_id
        else:
            query = """
            PREFIX ead: <http://www.exemplo.org/ead-ontologia#>
            SELECT ?curso ?titulo ?descricao ?duracao ?professor
            WHERE {
                ?curso a ead:Curso .
                OPTIONAL { ?curso ead:temTitulo ?titulo . }
                OPTIONAL { ?curso ead:temDescricao ?descricao . }
                OPTIONAL { ?curso ead:temDuracao ?duracao . }
                OPTIONAL { ?curso ead:ministradoPor ?professor . }
            }
            """
        
        return self.query(query)
    
    def get_student_tasks(self, student_id: str) -> List[Dict]:
        """
        Obtém tarefas de um estudante.
        
        Args:
            student_id: IRI do estudante
            
        Returns:
            Lista de tarefas
        """
        query = """
        PREFIX ead: <http://www.exemplo.org/ead-ontologia#>
        SELECT ?tarefa ?titulo ?dataEntrega ?avaliacao
        WHERE {
            <%s> ead:entregaTarefa ?tarefa .
            OPTIONAL { ?tarefa ead:temTitulo ?titulo . }
            OPTIONAL { ?tarefa ead:temDataEntrega ?dataEntrega . }
            OPTIONAL { ?avaliacao ead:possuiTarefa ?tarefa . }
        }
        """ % student_id
        
        return self.query(query)
    
    def get_resources_for_course(self, course_id: str) -> List[Dict]:
        """
        Obtém recursos de um curso.
        
        Args:
            course_id: IRI do curso
            
        Returns:
            Lista de recursos
        """
        query = """
        PREFIX ead: <http://www.exemplo.org/ead-ontologia#>
        SELECT ?recurso ?titulo ?url ?tipo
        WHERE {
            ?curso ead:possuiModulo ?modulo .
            ?modulo ead:possuiAula ?aula .
            ?aula ead:utilizaRecurso ?recurso .
            OPTIONAL { ?recurso ead:temTitulo ?titulo . }
            OPTIONAL { ?recurso ead:temURL ?url . }
            OPTIONAL { ?recurso rdf:type ?tipo . }
            FILTER (?curso = <%s>)
        }
        """ % course_id
        
        return self.query(query)
    
    def get_feedback(self, student_id: str) -> List[Dict]:
        """
        Obtém feedback recebido por um estudante.
        
        Args:
            student_id: IRI do estudante
            
        Returns:
            Lista de feedbacks
        """
        query = """
        PREFIX ead: <http://www.exemplo.org/ead-ontologia#>
        SELECT ?feedback ?texto ?professor
        WHERE {
            <%s> ead:recebeFeedback ?feedback .
            ?feedback ead:temTextoDeFeedback ?texto .
            ?professor ead:forneceFeedback ?feedback .
        }
        """ % student_id
        
        return self.query(query)
    
    def get_competencies_for_course(self, course_id: str) -> List[Dict]:
        """
        Obtém competências e resultados de aprendizagem de um curso.
        
        Args:
            course_id: IRI do curso
            
        Returns:
            Lista de competências
        """
        query = """
        PREFIX ead: <http://www.exemplo.org/ead-ontologia#>
        SELECT ?resultado ?competencia
        WHERE {
            <%s> ead:possuiResultadoDeAprendizagem ?resultado .
            ?resultado ead:possuiCompetencia ?competencia .
        }
        """ % course_id
        
        return self.query(query)
    
    def check_consistency(self, entity_iri: str, property_iri: str, value: str) -> bool:
        """
        Verifica consistência ontológica de uma afirmação.
        
        Args:
            entity_iri: IRI da entidade
            property_iri: IRI da propriedade
            value: Valor a verificar
            
        Returns:
            True se consistente, False caso contrário
        """
        # Verificar se a propriedade existe e se o domínio/range são compatíveis
        query = """
        PREFIX ead: <http://www.exemplo.org/ead-ontologia#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        ASK {
            <%s> rdf:type ?domain .
            <%s> rdfs:domain ?domain .
            <%s> rdfs:range ?range .
            ?value rdf:type ?range .
        }
        """ % (property_iri, property_iri, property_iri)
        
        result = self.graph.query(query)
        return bool(result)

