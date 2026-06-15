# Fluxos Principais do Usuário — Jaci

## Objetivo

Este documento descreve os principais fluxos de interação do usuário no Jaci, orientando decisões de produto, design, arquitetura e implementação.

Os fluxos estão organizados de acordo com sua relevância para o negócio e frequência de uso.

---

## Princípios Gerais

Todos os fluxos devem respeitar os seguintes princípios:

* Mobile-first
* Simplicidade operacional
* Colaboração em tempo real
* Funcionamento offline sempre que possível
* Separação entre planejamento e execução
* Preservação do histórico
* Aprendizado contínuo com confirmação explícita do usuário

---

# FL-01 — Primeiro Acesso e Onboarding

## Objetivo

Permitir que um novo usuário esteja apto a criar sua primeira lista em poucos minutos.

## Atores

* Usuário anônimo
* Sistema

## Fluxo Principal

```text
Acessar aplicação
    ↓
Autenticar (magic link ou e-mail/senha)
    ↓
Validar credenciais
    ↓
Criar usuário (primeiro acesso)
    ↓
Criar grupo padrão ("Minha Casa")
    ↓
Criar categorias padrão
    ↓
Exibir tela inicial
```

## Resultado Esperado

* Usuário autenticado
* Grupo criado
* Categorias disponíveis
* Ambiente pronto para uso

---

# FL-02 — Criação de Template

## Objetivo

Permitir que o usuário planeje compras recorrentes.

## Atores

* Usuário autenticado

## Fluxo Principal

```text
Acessar "Templates"
    ↓
Criar novo template
    ↓
Definir nome
    ↓
Definir recorrência
    ↓
Definir orçamento (opcional)
    ↓
Adicionar itens
    ↓
Definir categoria
    ↓
Definir quantidade planejada
    ↓
Adicionar observações (opcional)
    ↓
Salvar template
```

## Resultado Esperado

* Template ativo
* Itens organizados por categoria
* Compra pronta para execução futura

---

# FL-03 — Geração de Execução

## Objetivo

Criar uma compra concreta a partir de um template.

## Atores

* Usuário autenticado
* Sistema

## Fluxo Manual

```text
Selecionar template
    ↓
Gerar execução
    ↓
Escolher data
    ↓
Salvar execução
```

## Fluxo Automático

```text
Finalizar execução
    ↓
Calcular próxima recorrência
    ↓
Criar nova execução agendada
```

## Resultado Esperado

* Execução criada
* Compra disponível na agenda

---

# FL-04 — Execução da Compra

## Objetivo

Permitir que o usuário realize a compra com o menor atrito possível.

## Atores

* Usuário autenticado

## Fluxo Principal

```text
Abrir execução
    ↓
Iniciar compra
    ↓
Visualizar itens agrupados por categoria
    ↓
Marcar item como comprado
    ↓
Informar quantidade comprada
    ↓
Informar valor unitário
    ↓
Informar local de compra (opcional)
    ↓
Visualizar total acumulado
    ↓
Receber alertas de orçamento
    ↓
Adicionar itens esquecidos (opcional)
    ↓
Editar observações (opcional)
    ↓
Finalizar compra
```

## Cenários Alternativos

* Alterar quantidade planejada
* Remover item não concluído
* Trabalhar sem conexão
* Resolver conflitos de sincronização

## Resultado Esperado

* Compra registrada
* Histórico preservado
* Próximo ciclo preparado

---

# FL-05 — Compra Colaborativa

## Objetivo

Permitir que múltiplos usuários participem da mesma compra.

## Atores

* Membros do grupo
* Sistema

## Fluxo Principal

```text
Usuário inicia compra
    ↓
Sistema notifica membros
    ↓
Membros acessam execução
    ↓
Usuários atualizam itens simultaneamente
    ↓
Sistema sincroniza alterações
    ↓
Sistema detecta conflitos
    ↓
Qualquer membro finaliza compra
```

## Resultado Esperado

* Compra compartilhada
* Dados consistentes
* Histórico único

---

# FL-06 — Aprendizado do Template

## Objetivo

Reduzir retrabalho e manter os templates atualizados.

## Pré-condições

* Execução vinculada a um template
* Itens adicionados ou alterados durante a compra

## Fluxo Principal

```text
Finalizar compra
    ↓
Detectar itens criados durante a execução
    ↓
Detectar alterações recorrentes
    ↓
Exibir sugestões
    ↓
Usuário seleciona alterações desejadas
    ↓
Atualizar template
```

## Tipos de Sugestão

* Novos itens
* Ajuste de quantidade padrão
* Atualização de observações

## Resultado Esperado

* Template evolui com o uso
* Usuário reduz retrabalho

---

# FL-07 — Gestão de Grupos

## Objetivo

Permitir o compartilhamento de compras.

## Atores

* Usuário autenticado

## Fluxo Principal

```text
Criar grupo
    ↓
Convidar membros
    ↓
Enviar convite
    ↓
Aceitar convite
    ↓
Compartilhar templates e execuções
```

## Resultado Esperado

* Grupo ativo
* Colaboração habilitada

---

# FL-08 — Consulta da Agenda e Histórico

## Objetivo

Permitir acompanhamento das compras e dos gastos.

## Atores

* Usuário autenticado

## Fluxo Principal

```text
Acessar agenda
    ↓
Filtrar período
    ↓
Selecionar execução
    ↓
Visualizar detalhes
    ↓
Consultar histórico de preços
    ↓
Analisar gastos
```

## Resultado Esperado

* Histórico acessível
* Planejamento financeiro facilitado

---

# FL-09 — Operação Offline

## Objetivo

Garantir continuidade da compra em ambientes com conectividade limitada.

## Atores

* Usuário autenticado
* Sistema

## Fluxo Principal

```text
Perda de conexão
    ↓
Sistema identifica modo offline
    ↓
Usuário continua utilizando a execução
    ↓
Alterações são armazenadas localmente
    ↓
Conexão restabelecida
    ↓
Sistema sincroniza alterações
    ↓
Resolver conflitos (se necessário)
```

## Resultado Esperado

* Nenhuma alteração é perdida
* Experiência de compra ininterrupta

---

# Fluxo Crítico do Produto

O fluxo mais importante do Jaci é a execução da compra.

```text
Abrir execução
    ↓
Marcar itens
    ↓
Adicionar item esquecido
    ↓
Visualizar total
    ↓
Finalizar compra
```

Toda decisão de produto, arquitetura ou experiência do usuário deve priorizar este cenário.

Pergunta orientadora:

"Esta alteração torna a execução da compra mais rápida, simples ou confiável?"

---

# FL-10 — Home Operacional

## Objetivo

Permitir que o usuário identifique e acesse rapidamente a compra mais relevante.

## Fluxo Principal

```text
Acessar a Home
    ↓
Visualizar compra em andamento ou próxima compra
    ↓
Consultar indicadores e alertas do grupo ativo
    ↓
Iniciar ou continuar compra em um toque
    ↓
Consultar histórico recente ou usar ações rápidas
```

## Resultado Esperado

* Compra ativa acessível em um toque
* Próxima compra visível sem navegação adicional
* Problemas relevantes identificáveis rapidamente
* Estado de conexão sempre visível
