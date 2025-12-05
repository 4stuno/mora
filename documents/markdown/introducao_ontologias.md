# Introdução à Engenharia de Ontologias

## O que é uma Ontologia?

Uma ontologia é uma especificação formal e explícita de uma conceitualização compartilhada. No contexto da Web Semântica, ontologias são usadas para descrever o significado dos dados de forma que possam ser processados por máquinas.

## Componentes de uma Ontologia

### Classes
Classes representam conceitos ou categorias de entidades. Por exemplo, em uma ontologia educacional, podemos ter classes como `Curso`, `Estudante`, `Professor`, `Recurso`.

### Propriedades
Propriedades descrevem relações entre entidades ou atributos de entidades:
- **Propriedades de Objeto**: Relacionam duas entidades (ex: `matriculadoEm`)
- **Propriedades de Dados**: Relacionam entidades a valores literais (ex: `temTitulo`)

### Indivíduos
Indivíduos são instâncias específicas de classes. Por exemplo, `Estudante_Ana` é um indivíduo da classe `Estudante`.

## OWL 2 DL

OWL 2 DL (Description Logic) é uma variante do OWL 2 que oferece:
- Expressividade rica para modelagem
- Decidibilidade garantida
- Suporte a reasoners eficientes (HermiT, Pellet)

## Inferência em Ontologias

Reasoners DL podem inferir:
- **Classificação**: Hierarquia completa de classes
- **Realização**: Tipos de indivíduos baseados em propriedades
- **Consistência**: Verificação de contradições
- **Materialização**: Adição de triplas inferidas ao grafo

## Aplicações em EAD

Ontologias podem ser usadas para:
- Modelar conhecimento educacional
- Facilitar busca semântica
- Suportar sistemas de recomendação
- Garantir consistência de dados

**Fonte**: Material do curso "Introdução à Engenharia de Ontologias"  
**Data**: 2024  
**Tema**: Fundamentos de Ontologias

