# BL-0002 — Adicionar unidades de medida

## Identificação e entrada

| Campo | Valor |
| --- | --- |
| ID | `BL-0002` |
| Título | Adicionar unidades de medida |
| Tipo | `melhoria` |
| Estado | `recebido` |
| Severidade | `a_triar` |
| Prioridade | `a_definir` |
| Data de entrada | `2026-07-24` |
| Origem | Item 3 da ordem de prioridade do roadmap em `AGENTS.md` |
| Ambiente/versão | Estado de `develop` em `2026-07-24` |
| Responsável | `a_definir` |
| Atualizado em | `2026-07-24` |

### Comportamento observado

Itens de template e de execução armazenam quantidades numéricas, mas não
registram a unidade de medida correspondente. O significado de valores como
`1`, `2` ou `0,5` depende do entendimento dos membros do grupo.

### Comportamento esperado

O usuário deve poder planejar e registrar quantidades com unidades de medida
claras, preservando a simplicidade durante a compra, execuções históricas,
funcionamento offline e separação entre template e execução.

### Impacto e abrangência

- Impacto: quantidades podem ser ambíguas para itens comprados por peso, volume
  ou embalagem.
- Abrangência: itens de template, itens de execução, apresentação, histórico e
  sincronização offline.
- Frequência: sempre que a quantidade não representar uma unidade implícita.

### Passos de reprodução

Não há falha pontual a reproduzir. Crie um item cuja quantidade seja `0,5` e
observe que o sistema não registra se o valor representa quilograma, litro ou
outra unidade.

### Evidências sanitizadas

- [Roadmap do Jaci](../../../../AGENTS.md#ordem-de-prioridade-do-roadmap).
- [Entidades do domínio](../../entities.md).

### Workaround

Informar a unidade no nome ou nas observações do item, com risco de
inconsistência e retrabalho.

## Triagem

| Campo | Valor |
| --- | --- |
| Confirmação | `a_triar` |
| Classificação | `a_triar` |
| Domínio afetado | `a_triar` |
| Regras de negócio afetadas | `a_triar` |
| Risco de segurança | `a_avaliar` |
| Risco de LGPD | `a_avaliar` |
| Risco de isolamento por grupo | `a_avaliar` |
| Risco offline/sincronização | `a_avaliar` |
| Risco ao histórico financeiro | `a_avaliar` |
| Risco à recorrência | `a_avaliar` |
| Risco à separação template/execução | `a_avaliar` |
| Dependências | `a_triar` |
| Duplicidades | `a_triar` |
| Responsável pela próxima etapa | `a_definir` |
| Próximo passo | Realizar triagem da necessidade e dos impactos sobre dados existentes |

## Acompanhamento até produção

- Documento refinado: ainda não criado.
- Implementação (commits/PRs): ainda não iniciada.
- Validações: ainda não iniciadas.
- Publicação: ainda não publicada.
- Itens relacionados: nenhum definido antes da triagem.

### Impedimentos

- Nenhum registrado.

## Histórico

| Data/hora | Autor | Mudança | Motivo/evidência |
| --- | --- | --- | --- |
| `2026-07-24 00:48 -03` | Codex | Item criado em `recebido` | Migração do item aberto no roadmap legado |
