# Competency Questions (CQs)

Este documento lista as Competency Questions (CQs) que a ontologia deve ser capaz de responder através de inferência DL.

## CQ1: Quais estudantes estão matriculados em um curso específico?

**Tipo**: Consulta direta com inferência de hierarquia

**SPARQL**:
```sparql
PREFIX ead: <http://www.exemplo.org/ead-ontologia#>
SELECT ?estudante ?curso
WHERE {
    ?estudante a ead:Estudante .
    ?estudante ead:matriculadoEm ?curso .
    ?curso a ead:Curso .
}
```

**Axiomas DL utilizados**:
- Hierarquia: `Estudante rdfs:subClassOf Usuario`
- Propriedade: `matriculadoEm domain Estudante, range Curso`

**Dependência de inferência**: Inferência de tipo através de hierarquia

---

## CQ2: Quais recursos são utilizados em aulas de um módulo específico?

**Tipo**: Consulta transitiva com inferência de propriedade transitiva

**SPARQL**:
```sparql
PREFIX ead: <http://www.exemplo.org/ead-ontologia#>
SELECT ?recurso ?modulo
WHERE {
    ?curso ead:possuiModulo ?modulo .
    ?modulo ead:possuiAula ?aula .
    ?aula ead:utilizaRecurso ?recurso .
}
```

**Axiomas DL utilizados**:
- Propriedade transitiva: `possuiModulo owl:TransitiveProperty`
- Restrição existencial: `Aula rdfs:subClassOf (utilizaRecurso some Recurso)`

**Dependência de inferência**: Inferência transitiva de `possuiModulo`

---

## CQ3: Quais cursos são pré-requisitos diretos ou indiretos de um curso?

**Tipo**: Consulta transitiva

**SPARQL**:
```sparql
PREFIX ead: <http://www.exemplo.org/ead-ontologia#>
SELECT ?curso ?preRequisito
WHERE {
    ?curso ead:possuiPreRequisito+ ?preRequisito .
    ?preRequisito a ead:Curso .
}
```

**Axiomas DL utilizados**:
- Propriedade transitiva: `possuiPreRequisito owl:TransitiveProperty`

**Dependência de inferência**: Inferência transitiva de `possuiPreRequisito`

---

## CQ4: Quais estudantes receberam feedback de um professor específico?

**Tipo**: Consulta com propriedade inversa

**SPARQL**:
```sparql
PREFIX ead: <http://www.exemplo.org/ead-ontologia#>
SELECT ?estudante ?feedback ?texto
WHERE {
    ?professor a ead:Professor .
    ?professor ead:forneceFeedback ?feedback .
    ?estudante ead:recebeFeedback ?feedback .
    ?feedback ead:temTextoDeFeedback ?texto .
}
```

**Axiomas DL utilizados**:
- Propriedade inversa: `forneceFeedback owl:inverseOf recebeFeedback`

**Dependência de inferência**: Inferência através de propriedade inversa

---

## CQ5: Quais avaliações possuem tarefas que foram entregues por estudantes?

**Tipo**: Consulta com restrições existenciais

**SPARQL**:
```sparql
PREFIX ead: <http://www.exemplo.org/ead-ontologia#>
SELECT ?avaliacao ?tarefa ?estudante
WHERE {
    ?avaliacao a ead:Avaliacao .
    ?avaliacao ead:possuiTarefa ?tarefa .
    ?estudante a ead:Estudante .
    ?estudante ead:entregaTarefa ?tarefa .
}
```

**Axiomas DL utilizados**:
- Restrição existencial: `Questionario rdfs:subClassOf (possuiTarefa some Tarefa)`
- Hierarquia: `Questionario rdfs:subClassOf Avaliacao`

**Dependência de inferência**: Inferência de tipo através de hierarquia e restrições

---

## CQ6: Quais recursos de acessibilidade estão disponíveis para um recurso específico?

**Tipo**: Consulta com restrições de domínio/range

**SPARQL**:
```sparql
PREFIX ead: <http://www.exemplo.org/ead-ontologia#>
SELECT ?recurso ?recursoAcessibilidade
WHERE {
    ?recurso a ead:Recurso .
    ?recurso ead:possuiRecursoDeAcessibilidade ?recursoAcessibilidade .
    ?recursoAcessibilidade a ead:RecursoDeAcessibilidade .
}
```

**Axiomas DL utilizados**:
- Domain/Range: `possuiRecursoDeAcessibilidade domain Recurso, range RecursoDeAcessibilidade`

**Dependência de inferência**: Validação de tipos através de domain/range

---

## CQ7: Quais competências são desenvolvidas por um curso através de seus resultados de aprendizagem?

**Tipo**: Consulta com caminho de propriedades

**SPARQL**:
```sparql
PREFIX ead: <http://www.exemplo.org/ead-ontologia#>
SELECT ?curso ?resultado ?competencia
WHERE {
    ?curso a ead:Curso .
    ?curso ead:possuiResultadoDeAprendizagem ?resultado .
    ?resultado a ead:ResultadoDeAprendizagem .
    ?resultado ead:possuiCompetencia ?competencia .
    ?competencia a ead:Competencia .
}
```

**Axiomas DL utilizados**:
- Propriedades de objeto com domain/range coerentes

**Dependência de inferência**: Validação de tipos e caminhos

---

## CQ8: Quais cursos são ministrados por professores e possuem módulos?

**Tipo**: Consulta com múltiplas restrições existenciais

**SPARQL**:
```sparql
PREFIX ead: <http://www.exemplo.org/ead-ontologia#>
SELECT ?curso ?professor ?modulo
WHERE {
    ?curso a ead:Curso .
    ?curso ead:ministradoPor ?professor .
    ?professor a ead:Professor .
    ?curso ead:possuiModulo ?modulo .
    ?modulo a ead:Modulo .
}
```

**Axiomas DL utilizados**:
- Restrição existencial: `Curso rdfs:subClassOf (ministradoPor some Professor)`
- Restrição existencial: `Curso rdfs:subClassOf (possuiModulo some Modulo)`

**Dependência de inferência**: Inferência através de restrições existenciais

---

## CQ9: Quais estudantes possuem email e estão matriculados em cursos?

**Tipo**: Consulta com propriedades funcionais e hierarquia

**SPARQL**:
```sparql
PREFIX ead: <http://www.exemplo.org/ead-ontologia#>
SELECT ?estudante ?email ?curso
WHERE {
    ?estudante a ead:Estudante .
    ?estudante ead:matriculadoEm ?curso .
    ?perfil ead:temPapel ?papel .
    ?perfil ead:temEmail ?email .
}
```

**Axiomas DL utilizados**:
- Propriedade funcional: `temEmail owl:FunctionalProperty`
- Hierarquia: `Estudante rdfs:subClassOf Usuario`

**Dependência de inferência**: Inferência de propriedades funcionais

---

## CQ10: Verificar consistência: um estudante pode estar matriculado em um curso e não ter perfil de usuário?

**Tipo**: Verificação de consistência ontológica

**SPARQL**:
```sparql
PREFIX ead: <http://www.exemplo.org/ead-ontologia#>
ASK {
    ?estudante a ead:Estudante .
    ?estudante ead:matriculadoEm ?curso .
    FILTER NOT EXISTS {
        ?perfil ead:temPapel ?papel .
        ?papel a ead:Estudante .
    }
}
```

**Axiomas DL utilizados**:
- Hierarquia e restrições de domínio
- Verificação de inconsistências

**Dependência de inferência**: Verificação de consistência através de reasoner DL

---

## Mapeamento de CQs para Axiomas

| CQ | Axiomas DL Utilizados | Tipo de Inferência |
|----|----------------------|-------------------|
| CQ1 | Hierarquia, Domain/Range | Classificação |
| CQ2 | Propriedade Transitiva, Restrição Existencial | Transitividade |
| CQ3 | Propriedade Transitiva | Transitividade |
| CQ4 | Propriedade Inversa | Inversão |
| CQ5 | Hierarquia, Restrição Existencial | Classificação |
| CQ6 | Domain/Range | Validação de Tipos |
| CQ7 | Caminho de Propriedades | Validação de Caminhos |
| CQ8 | Múltiplas Restrições Existencias | Classificação |
| CQ9 | Propriedade Funcional, Hierarquia | Funcionalidade |
| CQ10 | Consistência Ontológica | Verificação de Consistência |

