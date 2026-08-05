# BL-0006 — Implementar integrações externas

## Identificação e entrada

| Campo | Valor |
| --- | --- |
| ID | `BL-0006` |
| Título | Implementar integrações externas |
| Tipo | `melhoria` |
| Estado | `recebido` |
| Severidade | `a_triar` |
| Prioridade | `a_definir` |
| Data de entrada | `2026-07-24` |
| Origem | Item 8 da ordem de prioridade do roadmap em `AGENTS.md` |
| Ambiente/versão | Estado de `develop` em `2026-07-24` |
| Responsável | `a_definir` |
| Atualizado em | `2026-07-24` |

### Comportamento observado

O Jaci usa serviços externos necessários à autenticação e ao envio de e-mails,
mas o roadmap registra uma frente genérica de integrações externas sem item
ativo, casos de uso ou sistemas de destino definidos.

### Comportamento esperado

As integrações que gerem valor ao planejamento ou à execução de compras devem
ser identificadas, priorizadas e implementadas sem comprometer funcionamento
offline, isolamento por grupo ou confiabilidade dos dados.

### Impacto e abrangência

- Impacto: oportunidades de interoperabilidade não possuem ponto único de
  triagem e acompanhamento.
- Abrangência: desconhecida até serem definidos sistemas e fluxos candidatos.
- Frequência: desconhecida.

### Passos de reprodução

Não se aplica como falha pontual. A demanda formaliza uma frente futura do
roadmap ainda sem escopo técnico.

### Evidências sanitizadas

- [Roadmap do Jaci](../../../../AGENTS.md#ordem-de-prioridade-do-roadmap).
- [README do projeto](../../../../README.md).

### Workaround

Usar os fluxos internos e as integrações já existentes para autenticação e
e-mail.

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
| Próximo passo | Realizar triagem dos casos de uso, sistemas candidatos e valor esperado |

## Acompanhamento até produção

- Documento refinado: ainda não criado.
- Implementação (commits/PRs): ainda não iniciada.
- Validações: ainda não iniciadas.
- Publicação: ainda não publicada.
- Itens relacionados: nenhum definido antes da triagem.

### Impedimentos

- Nenhum registrado; integrações candidatas permanecem a definir.

## Histórico

| Data/hora | Autor | Mudança | Motivo/evidência |
| --- | --- | --- | --- |
| `2026-07-24 00:48 -03` | Codex | Item criado em `recebido` | Migração do item aberto no roadmap legado |
