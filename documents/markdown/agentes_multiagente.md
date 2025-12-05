# Sistemas Multiagente para Educação

## Conceitos Fundamentais

Um Sistema Multiagente (MAS) é composto por múltiplos agentes autônomos que interagem para alcançar objetivos. Em educação, agentes podem representar:

- **Estudantes**: Agentes que executam tarefas e interagem com recursos
- **Professores**: Agentes que avaliam e fornecem feedback
- **Coordenadores**: Agentes que gerenciam fluxos e resolvem conflitos
- **Recomendadores**: Agentes que sugerem recursos e cursos

## Arquiteturas de Agentes

### Agentes Reativos
- Respostas diretas a estímulos
- Sem planejamento complexo
- Adequados para tarefas simples

### Agentes Deliberativos (BDI)
- **Beliefs**: Crenças sobre o estado do mundo
- **Desires**: Objetivos desejados
- **Intentions**: Planos de ação

### Agentes Híbridos
- Combinam reatividade e deliberação
- Adequados para ambientes dinâmicos

## Protocolos de Comunicação

### FIPA-ACL
- Padrão para comunicação entre agentes
- Performativas: `inform`, `request`, `propose`, `accept-proposal`

### Contract Net Protocol
- Para delegação de tarefas
- Coordenador envia `call-for-proposal`
- Agentes respondem com `propose`
- Coordenador aceita com `accept-proposal`

## LangGraph para Orquestração

LangGraph permite modelar fluxos complexos de agentes:
- **Estados**: Representam o estado compartilhado
- **Nós**: Representam agentes ou processos
- **Arestas**: Representam transições

## Benefícios em EAD

1. **Automação**: Tarefas rotineiras automatizadas
2. **Personalização**: Agentes adaptam-se a cada estudante
3. **Escalabilidade**: Sistema pode crescer com novos agentes
4. **Robustez**: Falhas isoladas não derrubam o sistema

**Fonte**: Material do curso "Sistemas Multiagente"  
**Data**: 2024  
**Tema**: Arquitetura de Agentes

