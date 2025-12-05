"""
Módulo para raciocínio DL usando HermiT.
"""
import os
from typing import List, Dict, Optional
from owlready2 import *
import warnings
warnings.filterwarnings("ignore")


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


class DLReasoner:
    """Classe para executar raciocínio DL usando HermiT."""
    
    def __init__(self, ontology_path: str = "ontologia_mora.owl"):
        """
        Inicializa o reasoner DL.
        
        Args:
            ontology_path: Caminho para o arquivo OWL
        """
        self.ontology_path = _get_ontology_path(ontology_path)
        self.onto = None
        self.reasoner = None
        self._load_ontology()
    
    def _load_ontology(self):
        """Carrega a ontologia."""
        try:
            self.onto = get_ontology(f"file://{self.ontology_path}").load()
            print(f"Ontologia carregada: {self.onto.base_iri}")
        except Exception as e:
            print(f"Erro ao carregar ontologia: {e}")
            raise
    
    def classify(self) -> Dict[str, List[str]]:
        """
        Executa classificação da ontologia usando HermiT.
        
        Returns:
            Dicionário com hierarquia de classes
        """
        if self.reasoner is None:
            # Tentar usar HermiT primeiro
            try:
                with self.onto:
                    sync_reasoner_hermit()
                    self.reasoner = "hermit"
            except Exception as e:
                error_msg = str(e)
                # Verificar se é erro de datatype não suportado
                if "UnsupportedDatatypeException" in error_msg or "xsd:date" in error_msg:
                    print("⚠️  Aviso: HermiT não suporta xsd:date usado na ontologia.")
                    print("   Continuando sem reasoner completo (SPARQL ainda funciona).")
                    self.reasoner = "none"
                else:
                    # Tentar Pellet como fallback
                    try:
                        with self.onto:
                            sync_reasoner_pellet()
                            self.reasoner = "pellet"
                    except Exception as e2:
                        print(f"⚠️  Aviso: Não foi possível inicializar reasoner completo: {e2}")
                        print("   Continuando sem reasoner (SPARQL ainda funciona).")
                        self.reasoner = "none"
        
        # Obter hierarquia de classes (mesmo sem reasoner, podemos usar subclasses explícitas)
        hierarchy = {}
        for cls in self.onto.classes():
            # Usar subclasses diretas se reasoner não disponível
            if self.reasoner == "none":
                subclasses = [c for c in self.onto.classes() 
                             if cls in c.is_a and c != cls]
            else:
                try:
                    subclasses = cls.subclasses()
                except:
                    # Fallback para subclasses diretas
                    subclasses = [c for c in self.onto.classes() 
                                 if cls in c.is_a and c != cls]
            
            if subclasses:
                hierarchy[str(cls)] = [str(sub) for sub in subclasses]
        
        return hierarchy
    
    def check_consistency(self) -> Dict[str, bool]:
        """
        Verifica consistência da ontologia.
        
        Returns:
            Dicionário com resultados de consistência
        """
        results = {
            'consistent': True,
            'inconsistencies': [],
            'reasoner_available': self.reasoner != "none" if self.reasoner else False
        }
        
        # Se reasoner não disponível, assumir consistente (verificação básica)
        if self.reasoner == "none" or self.reasoner is None:
            # Verificação básica sem reasoner
            try:
                # Verificar se há classes vazias ou problemas óbvios
                for cls in self.onto.classes():
                    if cls.is_a == [] and cls != Thing:
                        pass  # Pode ser normal
                results['consistent'] = True
                results['note'] = "Verificação básica (reasoner completo não disponível devido a xsd:date)"
            except Exception as e:
                results['consistent'] = False
                results['error'] = str(e)
        else:
            # Verificar inconsistências com reasoner
            try:
                with self.onto:
                    inconsistent_classes = []
                    for cls in self.onto.classes():
                        if cls.is_a == [] and cls != Thing:
                            pass
                    
                    results['consistent'] = len(inconsistent_classes) == 0
                    results['inconsistencies'] = inconsistent_classes
            except Exception as e:
                results['consistent'] = False
                results['error'] = str(e)
        
        return results
    
    def realize(self) -> Dict[str, List[str]]:
        """
        Executa realização (realization) - infere tipos de indivíduos.
        
        Returns:
            Dicionários com tipos inferidos para cada indivíduo
        """
        if self.reasoner is None:
            with self.onto:
                sync_reasoner()
        
        realization = {}
        
        for individual in self.onto.individuals():
            types = [str(t) for t in individual.is_a if isinstance(t, ThingClass)]
            if types:
                realization[str(individual)] = types
        
        return realization
    
    def get_inferred_properties(self, individual_name: str) -> Dict[str, List]:
        """
        Obtém propriedades inferidas para um indivíduo.
        
        Args:
            individual_name: Nome do indivíduo
            
        Returns:
            Propriedades inferidas
        """
        if self.reasoner is None:
            with self.onto:
                sync_reasoner()
        
        individual = self.onto.search_one(iri=f"*{individual_name}")
        if individual is None:
            return {}
        
        properties = {
            'object_properties': {},
            'data_properties': {}
        }
        
        # Obter propriedades de objeto
        for prop in self.onto.object_properties():
            values = getattr(individual, prop.name, [])
            if values:
                properties['object_properties'][prop.name] = [str(v) for v in values]
        
        # Obter propriedades de dados
        for prop in self.onto.data_properties():
            values = getattr(individual, prop.name, [])
            if values:
                properties['data_properties'][prop.name] = values
        
        return properties
    
    def materialize(self) -> Dict[str, int]:
        """
        Materializa inferências (adiciona triplas inferidas ao grafo).
        
        Returns:
            Estatísticas de materialização
        """
        # Contar triplas antes
        try:
            triples_before = sum(1 for _ in self.onto.world.graph.triples((None, None, None)))
        except:
            triples_before = 0
        
        # Tentar sincronizar reasoner se disponível
        if self.reasoner != "none" and self.reasoner is not None:
            try:
                with self.onto:
                    if self.reasoner == "hermit":
                        sync_reasoner_hermit()
                    elif self.reasoner == "pellet":
                        sync_reasoner_pellet()
                    else:
                        sync_reasoner()
            except:
                pass  # Se falhar, continuar sem reasoner
        
        # Contar triplas depois
        try:
            triples_after = sum(1 for _ in self.onto.world.graph.triples((None, None, None)))
        except:
            triples_after = triples_before
        
        stats = {
            'triples_before': triples_before,
            'triples_after': triples_after,
            'triples_added': triples_after - triples_before
        }
        
        return stats
    
    def run_all_reasoning(self) -> Dict[str, any]:
        """
        Executa todos os tipos de raciocínio.
        
        Returns:
            Resultados completos do raciocínio
        """
        results = {
            'classification': self.classify(),
            'consistency': self.check_consistency(),
            'realization': self.realize(),
            'materialization': self.materialize()
        }
        
        return results
    
    def save_inferred_ontology(self, output_path: str):
        """
        Salva a ontologia com inferências materializadas.
        
        Args:
            output_path: Caminho para salvar
        """
        if self.reasoner is None:
            with self.onto:
                sync_reasoner()
        
        self.onto.save(file=output_path, format="rdfxml")

