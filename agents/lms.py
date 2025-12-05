"""
LMSAgent - Gerencia estado da plataforma e triplestore.
"""
from typing import Dict, Any, Optional
from agents.base_agent import BaseAgent
from rag.sparql_query import SPARQLQueryEngine


class LMSAgent(BaseAgent):
    """Agente que mantém estado do curso e serve como interface para o triplestore."""
    
    def __init__(self, ontology_path: str = "ontologia_mora.owl", retriever=None):
        """
        Inicializa o agente LMS.
        
        Args:
            ontology_path: Caminho para a ontologia
            retriever: Retriever híbrido
        """
        super().__init__("LMSAgent", retriever)
        self.sparql_engine = SPARQLQueryEngine(ontology_path)
    
    def process(self, message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Processa consultas sobre o estado da plataforma.
        
        Args:
            message: Mensagem a processar
            context: Contexto adicional
            
        Returns:
            Resposta com informações da plataforma
        """
        # Detectar tipo de consulta
        message_lower = message.lower()
        
        # Consultas sobre cursos
        if any(word in message_lower for word in ['curso', 'course']):
            student_id = context.get('student_id') if context else None
            courses = self.sparql_engine.get_courses(student_id)
            
            response_content = "Cursos encontrados:\n\n"
            citations = {'documents': [], 'iris': []}
            
            for course in courses:
                titulo = course.get('titulo', course.get('tituloCurso', course.get('curso', 'N/A')))
                response_content += f"- {titulo}\n"
                if course.get('descricao'):
                    response_content += f"  Descrição: {course['descricao']}\n"
                if course.get('duracao'):
                    response_content += f"  Duração: {course['duracao']} horas\n"
                curso_iri = course.get('curso')
                if curso_iri and isinstance(curso_iri, str) and curso_iri.startswith('http'):
                    citations['iris'].append(curso_iri)
                response_content += "\n"
        
        # Consultas sobre tarefas
        elif any(word in message_lower for word in ['tarefa', 'task', 'tarefas', 'entregar']):
            # Tentar extrair estudante da mensagem ou usar padrão
            student_id = context.get('student_id') if context else None
            if not student_id and 'ana' in message_lower:
                student_id = "http://www.exemplo.org/ead-ontologia#Estudante_Ana"
            
            if student_id:
                tasks = self.sparql_engine.get_student_tasks(student_id)
                
                response_content = "Tarefas encontradas:\n\n"
                citations = {'documents': [], 'iris': []}
                
                if tasks:
                    for task in tasks:
                        titulo = task.get('titulo', task.get('tituloTarefa', task.get('tarefa', 'N/A')))
                        response_content += f"- {titulo}\n"
                        if task.get('dataEntrega'):
                            response_content += f"  Data de entrega: {task['dataEntrega']}\n"
                        tarefa_iri = task.get('tarefa')
                        if tarefa_iri and isinstance(tarefa_iri, str) and tarefa_iri.startswith('http'):
                            citations['iris'].append(tarefa_iri)
                        response_content += "\n"
                else:
                    response_content = "Nenhuma tarefa encontrada para este estudante."
            else:
                # Tentar buscar todas as tarefas
                query = """
                PREFIX ead: <http://www.exemplo.org/ead-ontologia#>
                SELECT ?tarefa ?titulo ?estudante
                WHERE {
                    ?estudante a ead:Estudante .
                    ?estudante ead:entregaTarefa ?tarefa .
                    OPTIONAL { ?tarefa ead:temTitulo ?titulo . }
                }
                LIMIT 10
                """
                results = self.sparql_engine.query(query)
                response_content = "Tarefas encontradas:\n\n"
                citations = {'documents': [], 'iris': []}
                for result in results:
                    titulo = result.get('titulo', result.get('tarefa', 'N/A'))
                    response_content += f"- {titulo}\n"
                    tarefa_iri = result.get('tarefa')
                    if tarefa_iri and isinstance(tarefa_iri, str) and tarefa_iri.startswith('http'):
                        citations['iris'].append(tarefa_iri)
                    response_content += "\n"
        
        # Consultas sobre recursos
        elif any(word in message_lower for word in ['recurso', 'resource', 'material']):
            course_id = context.get('course_id') if context else None
            if course_id:
                resources = self.sparql_engine.get_resources_for_course(course_id)
                
                response_content = "Recursos encontrados:\n\n"
                citations = {'iris': []}
                
                for resource in resources:
                    response_content += f"- {resource.get('titulo', resource.get('recurso', 'N/A'))}\n"
                    if resource.get('url'):
                        response_content += f"  URL: {resource['url']}\n"
                    if resource.get('recurso'):
                        citations['iris'].append({
                            'type': 'iri',
                            'iri': resource['recurso'],
                            'property': 'recurso'
                        })
                    response_content += "\n"
            else:
                response_content = "Por favor, forneça o ID do curso para consultar recursos."
                citations = {'documents': [], 'iris': []}
        
        else:
            response_content = "Como LMSAgent, posso ajudar com consultas sobre cursos, tarefas e recursos. Por favor, seja mais específico."
            citations = {'documents': [], 'iris': []}
        
        return self._format_response(response_content, citations)
    
    def execute_sparql(self, query: str) -> Dict[str, Any]:
        """
        Executa uma consulta SPARQL diretamente.
        
        Args:
            query: Consulta SPARQL
            
        Returns:
            Resultados da consulta
        """
        results = self.sparql_engine.query(query)
        
        citations = {
            'iris': []
        }
        
        # Extrair IRIs dos resultados
        for result in results:
            for value in result.values():
                if isinstance(value, str) and value.startswith('http://'):
                    citations['iris'].append({
                        'type': 'iri',
                        'iri': value
                    })
        
        return {
            'agent': self.name,
            'results': results,
            'citations': citations,
            'timestamp': self._get_timestamp()
        }

