# BL-0008 — Disponibilizar autoexclusão e anonimização de conta

## Identificação e entrada

| Campo | Valor |
| --- | --- |
| ID | `BL-0008` |
| Título | Disponibilizar autoexclusão e anonimização de conta |
| Tipo | `melhoria` |
| Estado | `pronto_para_refinamento` |
| Severidade | `N/A` |
| Prioridade | `P1` |
| Data de entrada | `2026-07-24` |
| Origem | Limitação do MVP registrada nos Termos de Uso e na Política de Privacidade |
| Ambiente/versão | Estado de `develop` em `2026-07-24` |
| Responsável | Engenharia Jaci |
| Atualizado em | `2026-08-05` |

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
| Confirmação | `confirmado` |
| Classificação | Melhoria de conformidade e experiência para integrar o Jaci ao fluxo central de solicitações LGPD e anonimizar a conta local sem apagar dados compartilhados ou históricos legítimos |
| Domínio afetado | Conta e perfil local, identidade Tupã, grupos e propriedade, autoria de execuções, auditoria, sessões e estado offline |
| Regras de negócio afetadas | Limitar a solicitação ao produto Jaci; preservar grupos e registros históricos após anonimização, inclusive quando o solicitante for o único membro; transferir ou desvincular propriedade sem cruzar grupos; não restaurar identificadores por sincronização; preservar recorrência e snapshots independentes de templates e execuções |
| Risco de segurança | Alto — solicitação, cancelamento e callback são operações sensíveis; exigem autenticação forte, validação integral do JWT do Tupã, idempotência, menor privilégio e revogação de sessões sem expor identificadores ou permitir exclusão de outra conta |
| Risco de LGPD | Alto — o fluxo exerce direitos do titular e precisa distinguir anonimização, eliminação e retenção legítima, registrar prazos e evidências e manter os documentos legais coerentes com o tratamento efetivo |
| Risco de isolamento por grupo | Alto — a conta pode participar ou ser proprietária de vários grupos; anonimização, transferência de propriedade e remoção de vínculos devem atuar somente nos grupos autorizados, sem revelar ou alterar dados de terceiros |
| Risco offline/sincronização | Alto — caches, filas e conflitos pendentes não podem reintroduzir dados pessoais nem continuar mutações autenticadas após a exclusão; a jornada deve informar que a solicitação e o cancelamento dependem de confirmação remota |
| Risco ao histórico financeiro | Alto — valores, itens e execuções compartilhados devem permanecer íntegros e atribuídos a uma identidade anonimizada, sem exclusão em cascata ou perda da rastreabilidade legítima |
| Risco à recorrência | Médio — anonimização e mudança de propriedade não podem recalcular ciclos, duplicar próximas execuções nem deixar processamento futuro dependente de uma conta desativada |
| Risco à separação template/execução | Médio — a anonimização não pode propagar mudanças entre templates e execuções nem remover snapshots e vínculos históricos existentes |
| Dependências | Fluxo do Tupã para `POST/GET /requests`, cancelamento, carência de 30 dias e saga; contrato de callback `DELETE /internal/users/{user_id}` autenticado por JWT e configuração do endpoint do Jaci; inventário local de identificadores e restrições referenciais; definição no refinamento de pseudonimização, propriedade de grupos, retenção, sessões, caches e filas offline |
| Duplicidades | Nenhuma identificada no Jaci; a saga e o contrato de exclusão já entregues pelo Tupã são dependências externas, não uma duplicidade desta adaptação local |
| Responsável pela próxima etapa | Engenharia Jaci |
| Próximo passo | Refinar a jornada mobile-first de solicitação, acompanhamento e cancelamento, o callback idempotente do Tupã, reautenticação, anonimização e propriedade de grupos, retenção, revogação de sessões, limpeza offline e atualização dos documentos legais |

## Acompanhamento até produção

- Documento refinado: ainda não criado.
- Implementação (commits/PRs): ainda não iniciada.
- Validações: triagem baseada nos Termos de Uso, na Política de Privacidade,
  nos modelos e vínculos referenciais do Jaci e no contrato de exclusão e na
  saga já disponíveis no Tupã; validações de implementação ainda não iniciadas.
- Publicação: ainda não publicada.
- Itens relacionados: contrato de exclusão de conta e saga do repositório Tupã.

### Impedimentos

- Nenhum registrado; os contratos necessários já existem no Tupã, e as regras
  detalhadas de retenção, pseudonimização e propriedade serão definidas no
  refinamento sem bloquear a promoção do item.

## Histórico

| Data/hora | Autor | Mudança | Motivo/evidência |
| --- | --- | --- | --- |
| `2026-07-24 00:48 -03` | Codex | Item criado em `recebido` | Migração da limitação de MVP documentada |
| `2026-08-05 22:24 -03` | Usuário/Codex | `recebido` -> `em_triagem` | Prioridade P1, escopo restrito ao Jaci e preservação anonimizada dos grupos confirmados; fluxo legal e integração existente com o Tupã confrontados |
| `2026-08-05 22:24 -03` | Codex | `em_triagem` -> `pronto_para_refinamento` | Classificação, riscos, dependências, duplicidades, responsável e próximo passo definidos |
