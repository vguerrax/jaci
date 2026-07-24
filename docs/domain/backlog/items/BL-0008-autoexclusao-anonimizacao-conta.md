# BL-0008 — Disponibilizar autoexclusão e anonimização de conta

## Identificação e entrada

| Campo | Valor |
| --- | --- |
| ID | `BL-0008` |
| Título | Disponibilizar autoexclusão e anonimização de conta |
| Tipo | `melhoria` |
| Estado | `recebido` |
| Severidade | `a_triar` |
| Prioridade | `a_definir` |
| Data de entrada | `2026-07-24` |
| Origem | Limitação do MVP registrada nos Termos de Uso e na Política de Privacidade |
| Ambiente/versão | Estado de `develop` em `2026-07-24` |
| Responsável | `a_definir` |
| Atualizado em | `2026-07-24` |

### Comportamento observado

O usuário não pode solicitar e acompanhar a exclusão da própria conta pela
aplicação. O fluxo atual depende de contato por escrito com o suporte e de
tratamento manual pelo operador.

### Comportamento esperado

O usuário deve dispor de fluxo seguro para solicitar exclusão e anonimização,
respeitando identidade centralizada no Tupã, vínculos em grupos compartilhados,
preservação legítima do histórico e prazos informados nos documentos legais.

### Impacto e abrangência

- Impacto: o exercício do direito depende de atendimento manual, com maior
  esforço e risco operacional.
- Abrangência: conta, identidade Tupã, dados pessoais, grupos compartilhados,
  histórico e auditoria.
- Frequência: sempre que um usuário solicita exclusão ou anonimização.

### Passos de reprodução

1. Acessar as opções de conta do usuário.
2. Procurar uma ação de exclusão ou solicitação de anonimização.
3. Observar que os Termos orientam contato externo com o suporte.

### Evidências sanitizadas

- [Termos de Uso](../../../../app/templates/pages/legal/terms.html).
- [Política de Privacidade](../../../../app/templates/pages/legal/privacy.html).

### Workaround

Enviar a solicitação por escrito ao canal de suporte informado nos documentos
legais e aguardar processamento manual.

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
| Próximo passo | Realizar triagem jurídica, de identidade, dados compartilhados e operação |

## Acompanhamento até produção

- Documento refinado: ainda não criado.
- Implementação (commits/PRs): ainda não iniciada.
- Validações: ainda não iniciadas.
- Publicação: ainda não publicada.
- Itens relacionados: nenhum definido antes da triagem.

### Impedimentos

- Nenhum registrado; contrato com o Tupã e regras de anonimização dependem da
  triagem.

## Histórico

| Data/hora | Autor | Mudança | Motivo/evidência |
| --- | --- | --- | --- |
| `2026-07-24 00:48 -03` | Codex | Item criado em `recebido` | Migração da limitação de MVP documentada |
